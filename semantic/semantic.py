from semantic.symbol_table import *


class SemanticAnalyzer:

    def __init__(self):

        self.sym_table = SymbolTable()

        self.errors = []

    def type_of(self, node):

        if node.kind == 'IntLit':
            return 'int'

        if node.kind == 'FloatLit':
            return 'float'

        if node.kind == 'StringLit':
            return 'string'

        if node.kind == 'Var':

            sym = self.sym_table.lookup(node.value)

            if not sym:

                self.errors.append(
                    f"[Semantic] Line {node.line}: Undeclared variable '{node.value}'"
                )

                return None

            return sym.type

        if node.kind == 'ArrayAccess':

            sym = self.sym_table.lookup(node.value)

            if not sym:

                self.errors.append(
                    f"[Semantic] Line {node.line}: Undeclared array '{node.value}'"
                )

                return None

            if not sym.is_array:

                self.errors.append(
                    f"[Semantic] Line {node.line}: '{node.value}' is not an array"
                )

            return sym.type

        if node.kind in ('BinOp', 'UnaryOp'):

            types = [self.type_of(c) for c in node.children]

            types = [t for t in types if t]

            if not types:
                return None

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

            sym = Symbol(
                name=node.value['name'],
                type=node.value['type'],
                scope='',
                initialized=bool(node.children)
            )

            if not self.sym_table.declare(sym):

                self.errors.append(
                    f"[Semantic] Line {node.line}: Redeclaration of '{sym.name}'"
                )

            if node.children:

                rhs_type = self.type_of(node.children[0])

                if rhs_type and rhs_type != sym.type:

                    if not (sym.type == 'float' and rhs_type == 'int'):

                        self.errors.append(
                            f"[Semantic] Line {node.line}: Type mismatch"
                        )

                self.analyze(node.children[0])

        elif k == 'ArrayDecl':

            sym = Symbol(
                name=node.value['name'],
                type=node.value['type'],
                scope='',
                is_array=True,
                array_size=node.value['size']
            )

            if not self.sym_table.declare(sym):

                self.errors.append(
                    f"[Semantic] Line {node.line}: Redeclaration of '{sym.name}'"
                )

        elif k == 'Assign':

            sym = self.sym_table.lookup(node.value['name'])

            if not sym:

                self.errors.append(
                    f"[Semantic] Line {node.line}: Undeclared variable '{node.value['name']}'"
                )

            else:

                sym.initialized = True

                rhs_type = self.type_of(node.children[0])

                if rhs_type and sym.type != rhs_type:

                    if not (sym.type == 'float' and rhs_type == 'int'):

                        self.errors.append(
                            f"[Semantic] Line {node.line}: Type mismatch in assignment"
                        )

                self.analyze(node.children[0])

        elif k in ('If', 'While', 'For', 'Print', 'BinOp', 'UnaryOp'):

            for c in node.children:
                self.analyze(c)

        elif k in ('Var', 'ArrayAccess'):

            self.type_of(node)