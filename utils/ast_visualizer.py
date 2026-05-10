from parser.ast_nodes import ASTNode


def print_ast(node, level=0):

    if node is None:
        return

    indent = "    " * level

    label = node.kind

    if node.value is not None:
        label += f" ({node.value})"

    print(indent + label)

    for child in node.children:

        if isinstance(child, ASTNode):
            print_ast(child, level + 1)