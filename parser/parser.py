from parser.ast_nodes import ASTNode
from lexer.tokens import Token


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def peek(self):

        if self.pos < len(self.tokens):
            return self.tokens[self.pos]

        return Token('EOF', '', 0)

    def consume(self, expected=None):

        tok = self.peek()

        if expected and tok.type != expected:

            self.errors.append(
                f"[Parser] Line {tok.line}: Expected '{expected}', got '{tok.value}' ({tok.type})"
            )

            return Token('ERROR', '', tok.line)

        self.pos += 1

        return tok

    def match(self, *types):
        return self.peek().type in types

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

            self.errors.append(
                f"[Parser] Line {tok.line}: Unexpected token '{tok.value}'"
            )

            self.consume()

            return ASTNode('Error')

    def parse_decl(self):

        type_tok = self.consume()

        name_tok = self.consume('ID')

        node = ASTNode(
            'Decl',
            value={
                'type': type_tok.value,
                'name': name_tok.value
            },
            line=type_tok.line
        )

        if self.match('LBRACKET'):

            self.consume('LBRACKET')

            size_tok = self.consume('INT_LIT')

            self.consume('RBRACKET')

            node.kind = 'ArrayDecl'

            node.value['size'] = int(size_tok.value)

            self.consume('SEMICOLON')

            return node

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

        node = ASTNode(
            'Assign',
            children=[expr],
            value={'name': name_tok.value},
            line=name_tok.line
        )

        if index:
            node.value['index'] = index

        return node

    def parse_if(self):

        tok = self.consume('IF')

        self.consume('LPAREN')

        cond = self.parse_expr()

        self.consume('RPAREN')

        then = self.parse_statement()

        node = ASTNode(
            'If',
            children=[cond, then],
            line=tok.line
        )

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

        return ASTNode(
            'While',
            children=[cond, body],
            line=tok.line
        )

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

        update = ASTNode(
            'Assign',
            children=[upd_expr],
            value={'name': upd_name.value},
            line=upd_name.line
        )

        body = self.parse_statement()

        return ASTNode(
            'For',
            children=[init, cond, update, body]
        )

    def parse_print(self):

        tok = self.consume('PRINT')

        self.consume('LPAREN')

        arg = self.parse_expr()

        self.consume('RPAREN')

        self.consume('SEMICOLON')

        return ASTNode(
            'Print',
            children=[arg],
            line=tok.line
        )

    def parse_block(self):

        tok = self.consume('LBRACE')

        node = ASTNode(
            'Block',
            line=tok.line
        )

        while not self.match('RBRACE', 'EOF'):

            node.children.append(
                self.parse_statement()
            )

        self.consume('RBRACE')

        return node

    def parse_expr(self):
        return self.parse_relational()

    def parse_relational(self):

        left = self.parse_additive()

        while self.match(
            'LT',
            'GT',
            'LE',
            'GE',
            'EQ',
            'NE'
        ):

            op = self.consume()

            right = self.parse_additive()

            left = ASTNode(
                'BinOp',
                children=[left, right],
                value=op.value,
                line=op.line
            )

        return left

    def parse_additive(self):

        left = self.parse_multiplicative()

        while self.match('PLUS', 'MINUS'):

            op = self.consume()

            right = self.parse_multiplicative()

            left = ASTNode(
                'BinOp',
                children=[left, right],
                value=op.value,
                line=op.line
            )

        return left

    def parse_multiplicative(self):

        left = self.parse_unary()

        while self.match('STAR', 'SLASH'):

            op = self.consume()

            right = self.parse_unary()

            left = ASTNode(
                'BinOp',
                children=[left, right],
                value=op.value,
                line=op.line
            )

        return left

    def parse_unary(self):

        if self.match('MINUS'):

            op = self.consume()

            return ASTNode(
                'UnaryOp',
                children=[self.parse_primary()],
                value='-',
                line=op.line
            )

        return self.parse_primary()

    def parse_primary(self):

        tok = self.peek()

        if tok.type == 'INT_LIT':

            self.consume()

            return ASTNode(
                'IntLit',
                value=int(tok.value),
                line=tok.line
            )

        elif tok.type == 'FLOAT_LIT':

            self.consume()

            return ASTNode(
                'FloatLit',
                value=float(tok.value),
                line=tok.line
            )

        elif tok.type == 'STRING_LIT':

            self.consume()

            return ASTNode(
                'StringLit',
                value=tok.value,
                line=tok.line
            )

        elif tok.type == 'ID':

            self.consume()

            if self.match('LBRACKET'):

                self.consume('LBRACKET')

                idx = self.parse_expr()

                self.consume('RBRACKET')

                return ASTNode(
                    'ArrayAccess',
                    children=[idx],
                    value=tok.value,
                    line=tok.line
                )

            return ASTNode(
                'Var',
                value=tok.value,
                line=tok.line
            )

        elif tok.type == 'LPAREN':

            self.consume('LPAREN')

            e = self.parse_expr()

            self.consume('RPAREN')

            return e

        else:

            self.errors.append(
                f"[Parser] Line {tok.line}: Unexpected token '{tok.value}' in expression"
            )

            self.consume()

            return ASTNode('Error')