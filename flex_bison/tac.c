#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ast.h"
#include "tac.h"

char tac[100][100];

int tacIndex = 0;

int tempCount = 1;

char* newTemp() {

    char *temp = malloc(10);

    sprintf(temp, "t%d", tempCount++);

    return temp;
}

char* generateExprTAC(ASTNode *node) {

    if (node == NULL)
        return "";

    // Leaf node
    if (node->left == NULL && node->right == NULL) {

        return strdup(node->value);
    }

    char *left = generateExprTAC(node->left);

    char *right = generateExprTAC(node->right);

    char *temp = newTemp();

    sprintf(
        tac[tacIndex++],
        "%s = %s %s %s",
        temp,
        left,
        node->value,
        right
    );

    return temp;
}

void generateTAC(ASTNode *root) {

    ASTNode *current = root;

    while (current != NULL) {

        if (strcmp(current->value, "=") == 0) {

            char *rhs = generateExprTAC(current->right);

            sprintf(
                tac[tacIndex++],
                "%s = %s",
                current->left->value,
                rhs
            );
        }

        current = current->next;
    }
}

void printTAC() {

    FILE *fp = fopen("tac.txt", "w");

    printf("\nTHREE ADDRESS CODE\n");
    printf("-------------------------\n");

    for (int i = 0; i < tacIndex; i++) {

        printf("%s\n", tac[i]);

        fprintf(fp, "%s\n", tac[i]);
    }

    fclose(fp);
}