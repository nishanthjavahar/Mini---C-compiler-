from parser.ast_nodes import ASTNode


class ConstantFolder:

    def fold(self, node):

        if node is None:
            return None

        # Recursively optimize children
        for i in range(len(node.children)):

            if isinstance(node.children[i], ASTNode):

                node.children[i] = self.fold(node.children[i])

        # Constant Folding
        if node.kind == 'BinOp':

            left = node.children[0]
            right = node.children[1]

            if left.kind == 'IntLit' and right.kind == 'IntLit':

                if node.value == '+':
                    return ASTNode('IntLit', value=left.value + right.value)

                elif node.value == '-':
                    return ASTNode('IntLit', value=left.value - right.value)

                elif node.value == '*':
                    return ASTNode('IntLit', value=left.value * right.value)

                elif node.value == '/':

                    if right.value != 0:

                        return ASTNode(
                            'IntLit',
                            value=left.value // right.value
                        )

        return node