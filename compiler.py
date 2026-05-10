"""
Mini-C Compiler
Stages: Lexical Analysis -> Syntax Analysis (AST) -> Semantic Analysis -> IR (TAC)
"""

import re
import sys
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple

# =============================================================
# STAGE 1: LEXER  (Tokenizer)
# =============================================================

KEYWORDS = {'int', 'float', 'if', 'else', 'while', 'for', 'print', 'return', 'void'}

TOKEN_SPEC = [
    ('FLOAT_LIT',  r'\d+\.\d+'),
    ('INT_LIT',    r'\d+'),
    ('STRING_LIT', r'"[^"]*"'),
    ('ID',         r'[A-Za-z_]\w*'),
    ('LBRACKET',   r'\['),
    ('RBRACKET',   r'\]'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('SEMICOLON',  r';'),
    ('COMMA',      r','),
    ('LE',         r'<='),
    ('GE',         r'>='),
    ('EQ',         r'=='),
    ('NE',         r'!='),
    ('LT',         r'<'),
    ('GT',         r'>'),
    ('ASSIGN',     r'='),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('STAR',       r'\*'),
    ('SLASH',      r'/'),
    ('NEWLINE',    r'\n'),
    ('SKIP',       r'[ \t\r]+'),
    ('COMMENT',    r'//[^\n]*'),
    ('MCOMMENT',   r'/\*.*?\*/'),
    ('MISMATCH',   r'.'),
]

TOKEN_RE = re.compile(
    '|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPEC),
    re.DOTALL
)


@dataclass
class Token:
    type: str
    value: str
    line: int


def tokenize(source: str):
    tokens, errors = [], []
    line = 1
    for mo in TOKEN_RE.finditer(source):
        kind = mo.lastgroup
        val  = mo.group()
        if kind == 'NEWLINE':
            line += 1
        elif kind in ('SKIP', 'COMMENT', 'MCOMMENT'):
            line += val.count('\n')
        elif kind == 'MISMATCH':
            errors.append(f"[Lexer] Line {line}: Unexpected character '{val}'")
        else:
            if kind == 'ID' and val in KEYWORDS:
                kind = val.upper()
            tokens.append(Token(kind, val, line))
    return tokens, errors


# =============================================================
# STAGE 2: PARSER  (Builds an AST)
# =============================================================

@dataclass
class ASTNode:
    kind:     str
    children: List[Any] = field(default_factory=list)
    value:    Any       = None
    line:     int       = 0


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0
        self.errors = []

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '', 0)

    def consume(self, expected=None):
        tok = self.peek()
        if expected and tok.type != expected:
            self.errors.append(
                f"[Parser] Line {tok.line}: Expected '{expected}', got '{tok.value}' ({tok.type})")
            return Token('ERROR', '', tok.line)
        self.pos += 1
        return tok

    def match(self, *types):
        return self.peek().type in types

    # ---------- top level ----------

    def parse_program(self):
        node = ASTNode('Program')
        while not self.match('EOF'):
            node.children.append(self.parse_statement())
        return node

    def parse_statement(self):
        tok = self.peek()
        if tok.type in ('INT', 'FLOAT'):
            return self.parse_decl()
        elif tok.type == 'IF':
            return self.parse_if()
        elif tok.type == 'WHILE':
            return self.parse_while()
        elif tok.type == 'FOR':
            return self.parse_for()
        elif tok.type == 'PRINT':
            return self.parse_print()
        elif tok.type == 'LBRACE':
            return self.parse_block()
        elif tok.type == 'ID':
            return self.parse_assign_stmt()
        else:
            self.errors.append(f"[Parser] Line {tok.line}: Unexpected token '{tok.value}'")
            self.consume()
            return ASTNode('Error')

    def parse_decl(self):
        type_tok = self.consume()
        name_tok = self.consume('ID')
        node = ASTNode('Decl', value={'type': type_tok.value, 'name': name_tok.value}, line=type_tok.line)
        # Array declaration: int arr[10];
        if self.match('LBRACKET'):
            self.consume('LBRACKET')
            size_tok = self.consume('INT_LIT')
            self.consume('RBRACKET')
            node.kind = 'ArrayDecl'
            node.value['size'] = int(size_tok.value)
            self.consume('SEMICOLON')
            return node
        # Variable with initializer: int x = 5;
        if self.match('ASSIGN'):
            self.consume('ASSIGN')
            node.children.append(self.parse_expr())
        self.consume('SEMICOLON')
        return node

    def parse_assign_stmt(self):
        name_tok = self.consume('ID')
        index = None
        if self.match('LBRACKET'):
            self.consume('LBRACKET')
            index = self.parse_expr()
            self.consume('RBRACKET')
        self.consume('ASSIGN')
        expr = self.parse_expr()
        self.consume('SEMICOLON')
        node = ASTNode('Assign', children=[expr], value={'name': name_tok.value}, line=name_tok.line)
        if index:
            node.value['index'] = index
        return node

    def parse_if(self):
        tok = self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_expr()
        self.consume('RPAREN')
        then = self.parse_statement()
        node = ASTNode('If', children=[cond, then], line=tok.line)
        if self.match('ELSE'):
            self.consume('ELSE')
            node.children.append(self.parse_statement())
        return node

    def parse_while(self):
        tok = self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_expr()
        self.consume('RPAREN')
        body = self.parse_statement()
        return ASTNode('While', children=[cond, body], line=tok.line)

    def parse_for(self):
        self.consume('FOR')
        self.consume('LPAREN')
        if self.match('INT', 'FLOAT'):
            init = self.parse_decl()
        elif self.match('ID'):
            init = self.parse_assign_stmt()
        else:
            self.consume('SEMICOLON')
            init = ASTNode('Empty')
        cond = self.parse_expr()
        self.consume('SEMICOLON')
        upd_name = self.consume('ID')
        self.consume('ASSIGN')
        upd_expr = self.parse_expr()
        self.consume('RPAREN')
        update = ASTNode('Assign', children=[upd_expr], value={'name': upd_name.value}, line=upd_name.line)
        body = self.parse_statement()
        return ASTNode('For', children=[init, cond, update, body])

    def parse_print(self):
        tok = self.consume('PRINT')
        self.consume('LPAREN')
        arg = self.parse_expr()
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return ASTNode('Print', children=[arg], line=tok.line)

    def parse_block(self):
        tok = self.consume('LBRACE')
        node = ASTNode('Block', line=tok.line)
        while not self.match('RBRACE', 'EOF'):
            node.children.append(self.parse_statement())
        self.consume('RBRACE')
        return node

    # ---------- expressions (with precedence) ----------

    def parse_expr(self):
        return self.parse_relational()

    def parse_relational(self):
        left = self.parse_additive()
        while self.match('LT', 'GT', 'LE', 'GE', 'EQ', 'NE'):
            op    = self.consume()
            right = self.parse_additive()
            left  = ASTNode('BinOp', children=[left, right], value=op.value, line=op.line)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.match('PLUS', 'MINUS'):
            op    = self.consume()
            right = self.parse_multiplicative()
            left  = ASTNode('BinOp', children=[left, right], value=op.value, line=op.line)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.match('STAR', 'SLASH'):
            op    = self.consume()
            right = self.parse_unary()
            left  = ASTNode('BinOp', children=[left, right], value=op.value, line=op.line)
        return left

    def parse_unary(self):
        if self.match('MINUS'):
            op = self.consume()
            return ASTNode('UnaryOp', children=[self.parse_primary()], value='-', line=op.line)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.type == 'INT_LIT':
            self.consume()
            return ASTNode('IntLit', value=int(tok.value), line=tok.line)
        elif tok.type == 'FLOAT_LIT':
            self.consume()
            return ASTNode('FloatLit', value=float(tok.value), line=tok.line)
        elif tok.type == 'STRING_LIT':
            self.consume()
            return ASTNode('StringLit', value=tok.value, line=tok.line)
        elif tok.type == 'ID':
            self.consume()
            if self.match('LBRACKET'):
                self.consume('LBRACKET')
                idx = self.parse_expr()
                self.consume('RBRACKET')
                return ASTNode('ArrayAccess', children=[idx], value=tok.value, line=tok.line)
            return ASTNode('Var', value=tok.value, line=tok.line)
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            e = self.parse_expr()
            self.consume('RPAREN')
            return e
        else:
            self.errors.append(f"[Parser] Line {tok.line}: Unexpected token '{tok.value}' in expression")
            self.consume()
            return ASTNode('Error')


# =============================================================
# STAGE 3: SEMANTIC ANALYSIS  (Type checking + Symbol Table)
# =============================================================

@dataclass
class Symbol:
    name:       str
    type:       str
    scope:      str
    is_array:   bool         = False
    array_size: Optional[int] = None
    initialized: bool        = False


class SymbolTable:
    def __init__(self):
        self.scopes:      List[Dict[str, Symbol]] = [{}]
        self.all_symbols: List[Symbol]            = []

    def push_scope(self): self.scopes.append({})
    def pop_scope(self):  self.scopes.pop()

    def current_scope_name(self):
        return f"scope_{len(self.scopes) - 1}"

    def declare(self, sym: Symbol):
        top = self.scopes[-1]
        if sym.name in top:
            return False          # already declared in this scope
        sym.scope = self.current_scope_name()
        top[sym.name] = sym
        self.all_symbols.append(sym)
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def to_table(self):
        rows = []
        for s in self.all_symbols:
            t = f"{s.type}[{s.array_size}]" if s.is_array else s.type
            rows.append({
                'name':        s.name,
                'type':        t,
                'scope':       s.scope,
                'initialized': s.initialized
            })
        return rows


class SemanticAnalyzer:
    def __init__(self):
        self.sym_table = SymbolTable()
        self.errors: List[str] = []

    def type_of(self, node) -> Optional[str]:
        if node.kind == 'IntLit':    return 'int'
        if node.kind == 'FloatLit':  return 'float'
        if node.kind == 'StringLit': return 'string'
        if node.kind == 'Var':
            sym = self.sym_table.lookup(node.value)
            if not sym:
                self.errors.append(f"[Semantic] Line {node.line}: Undeclared variable '{node.value}'")
                return None
            return sym.type
        if node.kind == 'ArrayAccess':
            sym = self.sym_table.lookup(node.value)
            if not sym:
                self.errors.append(f"[Semantic] Line {node.line}: Undeclared array '{node.value}'")
                return None
            if not sym.is_array:
                self.errors.append(f"[Semantic] Line {node.line}: '{node.value}' is not an array")
            return sym.type
        if node.kind in ('BinOp', 'UnaryOp'):
            types = [self.type_of(c) for c in node.children]
            types = [t for t in types if t]
            if not types: return None
            return 'float' if 'float' in types else 'int'
        return None

    def analyze(self, node):
        k = node.kind
        if k == 'Program':
            for c in node.children:
                self.analyze(c)

        elif k == 'Block':
            self.sym_table.push_scope()
            for c in node.children:
                self.analyze(c)
            self.sym_table.pop_scope()

        elif k == 'Decl':
            sym = Symbol(name=node.value['name'], type=node.value['type'],
                         scope='', initialized=bool(node.children))
            if not self.sym_table.declare(sym):
                self.errors.append(f"[Semantic] Line {node.line}: Redeclaration of '{sym.name}'")
            if node.children:
                rhs_type = self.type_of(node.children[0])
                if rhs_type and rhs_type != sym.type:
                    if not (sym.type == 'float' and rhs_type == 'int'):
                        self.errors.append(
                            f"[Semantic] Line {node.line}: Type mismatch — cannot assign {rhs_type} to {sym.type}")
                self.analyze(node.children[0])

        elif k == 'ArrayDecl':
            sym = Symbol(name=node.value['name'], type=node.value['type'],
                         scope='', is_array=True, array_size=node.value['size'])
            if not self.sym_table.declare(sym):
                self.errors.append(f"[Semantic] Line {node.line}: Redeclaration of '{sym.name}'")

        elif k == 'Assign':
            sym = self.sym_table.lookup(node.value['name'])
            if not sym:
                self.errors.append(f"[Semantic] Line {node.line}: Undeclared variable '{node.value['name']}'")
            else:
                sym.initialized = True
                rhs_type = self.type_of(node.children[0])
                if rhs_type and sym.type != rhs_type:
                    if not (sym.type == 'float' and rhs_type == 'int'):
                        self.errors.append(
                            f"[Semantic] Line {node.line}: Type mismatch in assignment to '{sym.name}'")
                self.analyze(node.children[0])

        elif k == 'If':
            self.analyze(node.children[0])
            self.sym_table.push_scope()
            self.analyze(node.children[1])
            self.sym_table.pop_scope()
            if len(node.children) > 2:
                self.sym_table.push_scope()
                self.analyze(node.children[2])
                self.sym_table.pop_scope()

        elif k in ('While', 'For'):
            for c in node.children:
                if c.kind == 'Block':
                    self.sym_table.push_scope()
                    self.analyze(c)
                    self.sym_table.pop_scope()
                else:
                    self.analyze(c)

        elif k == 'Print':
            for c in node.children:
                self.analyze(c)

        elif k in ('BinOp', 'UnaryOp'):
            for c in node.children:
                self.analyze(c)

        elif k in ('Var', 'ArrayAccess'):
            self.type_of(node)


# =============================================================
# STAGE 4: THREE-ADDRESS CODE  (Intermediate Representation)
# =============================================================

class TACGenerator:
    def __init__(self):
        self.code:    List[str] = []
        self.temp_n:  int       = 0
        self.label_n: int       = 0

    def new_temp(self):
        self.temp_n += 1
        return f"t{self.temp_n}"

    def new_label(self):
        self.label_n += 1
        return f"L{self.label_n}"

    def emit(self, instr: str):
        self.code.append(instr)

    def gen(self, node) -> Optional[str]:
        k = node.kind

        if k == 'Program':
            for c in node.children:
                self.gen(c)

        elif k == 'Block':
            for c in node.children:
                self.gen(c)

        elif k == 'Decl':
            if node.children:
                rhs = self.gen(node.children[0])
                self.emit(f"{node.value['name']} = {rhs}")

        elif k == 'ArrayDecl':
            self.emit(f"alloc {node.value['name']}[{node.value['size']}]")

        elif k == 'Assign':
            rhs  = self.gen(node.children[0])
            name = node.value['name']
            if 'index' in node.value:
                idx = self.gen(node.value['index'])
                self.emit(f"{name}[{idx}] = {rhs}")
            else:
                self.emit(f"{name} = {rhs}")

        elif k == 'BinOp':
            l = self.gen(node.children[0])
            r = self.gen(node.children[1])
            t = self.new_temp()
            self.emit(f"{t} = {l} {node.value} {r}")
            return t

        elif k == 'UnaryOp':
            operand = self.gen(node.children[0])
            t       = self.new_temp()
            self.emit(f"{t} = -{operand}")
            return t

        elif k == 'If':
            cond     = self.gen(node.children[0])
            else_lbl = self.new_label()
            end_lbl  = self.new_label()
            self.emit(f"ifFalse {cond} goto {else_lbl}")
            self.gen(node.children[1])
            if len(node.children) > 2:
                self.emit(f"goto {end_lbl}")
                self.emit(f"{else_lbl}:")
                self.gen(node.children[2])
                self.emit(f"{end_lbl}:")
            else:
                self.emit(f"{else_lbl}:")

        elif k == 'While':
            start_lbl = self.new_label()
            end_lbl   = self.new_label()
            self.emit(f"{start_lbl}:")
            cond = self.gen(node.children[0])
            self.emit(f"ifFalse {cond} goto {end_lbl}")
            self.gen(node.children[1])
            self.emit(f"goto {start_lbl}")
            self.emit(f"{end_lbl}:")

        elif k == 'For':
            self.gen(node.children[0])         # init
            start_lbl = self.new_label()
            end_lbl   = self.new_label()
            self.emit(f"{start_lbl}:")
            cond = self.gen(node.children[1])  # condition
            self.emit(f"ifFalse {cond} goto {end_lbl}")
            self.gen(node.children[3])         # body
            self.gen(node.children[2])         # update
            self.emit(f"goto {start_lbl}")
            self.emit(f"{end_lbl}:")

        elif k == 'Print':
            arg = self.gen(node.children[0])
            self.emit(f"print {arg}")

        elif k == 'IntLit':    return str(node.value)
        elif k == 'FloatLit':  return str(node.value)
        elif k == 'StringLit': return node.value
        elif k == 'Var':       return node.value

        elif k == 'ArrayAccess':
            idx = self.gen(node.children[0])
            t   = self.new_temp()
            self.emit(f"{t} = {node.value}[{idx}]")
            return t

        return None


# =============================================================
# MAIN PIPELINE  (ties all 4 stages together)
# =============================================================

def compile_minic(source: str) -> dict:
    result = {
        'tokens':       [],
        'symbol_table': [],
        'tac':          [],
        'errors':       [],
    }

    # --- Stage 1: Lexical Analysis ---
    tokens, lex_errors = tokenize(source)
    result['errors'].extend(lex_errors)
    result['tokens'] = [
        {'type': t.type, 'value': t.value, 'line': t.line}
        for t in tokens
    ]

    # --- Stage 2: Syntax Analysis (parse to AST) ---
    parser = Parser(tokens)
    ast    = parser.parse_program()
    result['errors'].extend(parser.errors)

    # --- Stage 3: Semantic Analysis ---
    sem = SemanticAnalyzer()
    sem.analyze(ast)
    result['errors'].extend(sem.errors)
    result['symbol_table'] = sem.sym_table.to_table()

    # --- Stage 4: Generate Three-Address Code ---
    tac_gen = TACGenerator()
    tac_gen.gen(ast)
    result['tac'] = tac_gen.code

    return result


# =============================================================
# PRETTY PRINTER  (formats the output nicely)
# =============================================================

def print_results(result: dict):
    # ---- TOKENS ----
    print("=" * 60)
    print("  STAGE 1: TOKENS")
    print("=" * 60)
    print(f"{'LINE':<6} {'TYPE':<15} {'VALUE'}")
    print("-" * 40)
    for tok in result['tokens']:
        print(f"{tok['line']:<6} {tok['type']:<15} {tok['value']}")

    # ---- SYMBOL TABLE ----
    print("\n" + "=" * 60)
    print("  STAGE 3: SYMBOL TABLE")
    print("=" * 60)
    if result['symbol_table']:
        print(f"{'NAME':<15} {'TYPE':<12} {'SCOPE':<12} {'INITIALIZED'}")
        print("-" * 50)
        for sym in result['symbol_table']:
            init = "Yes" if sym['initialized'] else "No"
            print(f"{sym['name']:<15} {sym['type']:<12} {sym['scope']:<12} {init}")
    else:
        print("  (no symbols declared)")

    # ---- THREE-ADDRESS CODE ----
    print("\n" + "=" * 60)
    print("  STAGE 4: THREE-ADDRESS CODE (TAC / IR)")
    print("=" * 60)
    if result['tac']:
        for i, line in enumerate(result['tac'], 1):
            print(f"  {i:>3}:  {line}")
    else:
        print("  (no instructions generated)")

    # ---- ERRORS ----
    print("\n" + "=" * 60)
    print("  ERRORS")
    print("=" * 60)
    if result['errors']:
        for err in result['errors']:
            print(f"  *** {err}")
    else:
        print("  No errors found. Compilation successful!")
    print("=" * 60)


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == '__main__':
    # Usage:  python compiler.py test_program.mc
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file.mc>")
        print("Example: python compiler.py test_program.mc")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    print(f"\nCompiling: {filename}\n")
    output = compile_minic(source_code)
    print_results(output)