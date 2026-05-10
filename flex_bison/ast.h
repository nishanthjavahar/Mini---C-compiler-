#ifndef AST_H
#define AST_H

#include <stdio.h>

typedef struct ASTNode {

    char value[100];

    struct ASTNode *left;
    struct ASTNode *right;

    struct ASTNode *next;

} ASTNode;

ASTNode* createNode(char *label);

void printAST(ASTNode *root, int level);

void generateDOT(ASTNode *root, FILE *fp);

#endif