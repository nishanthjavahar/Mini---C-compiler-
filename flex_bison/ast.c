#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ast.h"

ASTNode* createNode(char *label) {

    ASTNode *node = malloc(sizeof(ASTNode));

    strcpy(node->value, label);

    node->left = NULL;
    node->next = NULL;
    node->right = NULL;

    return node;
}

void printAST(ASTNode *node, int level) {

    if (node == NULL)
        return;

    for (int i = 0; i < level; i++) {
        printf("│   ");
    }

    printf("├── %s\n", node->value);

    printAST(node->left, level + 1);
    printAST(node->right, level + 1);

    // PRINT NEXT STATEMENT
    printAST(node->next, level);
}

void generateDOT(ASTNode *root, FILE *fp) {

    if (root == NULL)
        return;

    fprintf(
        fp,
        "\"%p\" [label=\"%s\"];\n",
        root,
        root->value
    );

    if (root->left) {

        fprintf(
            fp,
            "\"%p\" -> \"%p\";\n",
            root,
            root->left
        );

        generateDOT(root->left, fp);
    }

    if (root->right) {

        fprintf(
            fp,
            "\"%p\" -> \"%p\";\n",
            root,
            root->right
        );

        generateDOT(root->right, fp);
    }

    if (root->next) {

        fprintf(
            fp,
            "\"%p\" -> \"%p\" [color=blue];\n",
            root,
            root->next
        );

        generateDOT(root->next, fp);
    }
}
