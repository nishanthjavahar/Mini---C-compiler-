class TACGenerator:

    def __init__(self):

        self.code = []

        self.temp_n = 0

        self.label_n = 0

    def new_temp(self):

        self.temp_n += 1

        return f"t{self.temp_n}"

    def new_label(self):

        self.label_n += 1

        return f"L{self.label_n}"

    def emit(self, instr):

        self.code.append(instr)

    def gen(self, node):

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

            self.emit(
                f"alloc {node.value['name']}[{node.value['size']}]"
            )

        elif k == 'Assign':

            rhs = self.gen(node.children[0])

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

            t = self.new_temp()

            self.emit(f"{t} = -{operand}")

            return t

        elif k == 'If':

            cond = self.gen(node.children[0])

            else_lbl = self.new_label()

            end_lbl = self.new_label()

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

            end_lbl = self.new_label()

            self.emit(f"{start_lbl}:")

            cond = self.gen(node.children[0])

            self.emit(f"ifFalse {cond} goto {end_lbl}")

            self.gen(node.children[1])

            self.emit(f"goto {start_lbl}")

            self.emit(f"{end_lbl}:")

        elif k == 'Print':

            arg = self.gen(node.children[0])

            self.emit(f"print {arg}")

        elif k == 'IntLit':
            return str(node.value)

        elif k == 'FloatLit':
            return str(node.value)

        elif k == 'StringLit':
            return node.value

        elif k == 'Var':
            return node.value

        elif k == 'ArrayAccess':

            idx = self.gen(node.children[0])

            t = self.new_temp()

            self.emit(f"{t} = {node.value}[{idx}]")

            return t