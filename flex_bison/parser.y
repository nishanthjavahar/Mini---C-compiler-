%{

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "symbol_table.h"
#include "tac.h"
#include "ast.h"

void yyerror(const char *s);

int yylex();

ASTNode *root;

int hasError = 0;

ASTNode *programRoot = NULL;
ASTNode *root = NULL;
ASTNode *lastNode = NULL;

%}

%union {

    int num;

    char *str;

    ASTNode *node;
}
%token INT FLOAT IF ELSE WHILE PRINT
%token PLUS MINUS MUL DIV ASSIGN
%token LT GT LE GE EQ NE
%token SEMICOLON
%token LPAREN RPAREN
%token LBRACE RBRACE
%token LBRACKET RBRACKET
%token <num> NUMBER
%token <str> ID
%type <node> expression term factor
%%
program:
    statements
    ;

statements:
      statements statement
    |
    ;
statement:
      declaration
    | assignment
    | print_stmt
    | while_stmt
    | if_stmt
    ;

declaration:
      INT ID SEMICOLON
        {
            addSymbol($2, "int");
            printf(
                "Declaration: int %s\n",
                $2
            );
        }
    | FLOAT ID SEMICOLON
        {
            addSymbol($2, "float");
            printf(
                "Declaration: float %s\n",
                $2
            );
        }
    | INT ID LBRACKET NUMBER RBRACKET SEMICOLON
        {
            addSymbol($2, "int_array");
            printf(
                "Array Declaration: int %s[%d]\n",
                $2,
                $4
            );
        }
    ;
assignment:
    ID ASSIGN expression SEMICOLON
    {
        if (!symbolExists($1)) {
            FILE *fp = fopen("error.txt", "w");
            fprintf(
                fp,
                "Semantic Error: Variable '%s' not declared\n",
                $1
            );

            fclose(fp);

            printf(
                "Semantic Error: Variable '%s' not declared\n",
                $1
            );

            hasError = 1;

            return 0;
        }

        char *varType = getType($1);

        if (
            strcmp(varType, "int") == 0 &&
            strstr($3->value, ".") != NULL
        ) {

            FILE *fp = fopen("error.txt", "w");

            fprintf(
                fp,
                "Semantic Error: Type mismatch assigning float to int\n"
            );

            fclose(fp);

            printf(
                "Semantic Error: Type mismatch assigning float to int\n"
            );

            hasError = 1;

            return 0;
        }

        ASTNode *assign = createNode("=");

        ASTNode *idnode = createNode($1);

        assign->left = idnode;

        assign->right = $3;

        if (programRoot == NULL) {

            programRoot = assign;
            lastNode = assign;
        }
        else {

            lastNode->next = assign;
            lastNode = assign;
        }

        root = programRoot;

        printf("Assignment Parsed\n");
    }
;

print_stmt:

    PRINT LPAREN expression RPAREN SEMICOLON

    {
        printf("Print statement\n");
    }
    ;

while_stmt:

    WHILE LPAREN expression RPAREN LBRACE statements RBRACE

    {
        printf("While loop\n");
    }
    ;

if_stmt:

    IF LPAREN expression RPAREN LBRACE statements RBRACE

    {
        printf("If statement\n");
    }
    ;

expression:

      expression PLUS term

        {
            ASTNode *node = createNode("+");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression MINUS term

        {
            ASTNode *node = createNode("-");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression LT term

        {
            ASTNode *node = createNode("<");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression GT term

        {
            ASTNode *node = createNode(">");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression LE term

        {
            ASTNode *node = createNode("<=");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression GE term

        {
            ASTNode *node = createNode(">=");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression EQ term

        {
            ASTNode *node = createNode("==");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | expression NE term

        {
            ASTNode *node = createNode("!=");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | term

        {
            $$ = $1;
        }
;

term:

      term MUL factor

        {
            ASTNode *node = createNode("*");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | term DIV factor

        {
            ASTNode *node = createNode("/");

            node->left = $1;
            node->right = $3;

            $$ = node;
        }

    | factor

        {
            $$ = $1;
        }
;

factor:

      NUMBER

        {
            char buffer[20];

            sprintf(buffer, "%d", $1);

            $$ = createNode(strdup(buffer));
        }

    | ID

        {
            $$ = createNode($1);
        }

    | LPAREN expression RPAREN

        {
            $$ = $2;
        }
;

%%

void yyerror(const char *s) {

    FILE *fp = fopen("error.txt", "w");

    fprintf(
        fp,
        "Syntax Error: %s\n",
        s
    );

    fclose(fp);

    printf(
        "Syntax Error: %s\n",
        s
    );

    hasError = 1;
}

int main() {
    remove("ast.png");

remove("ast.dot");

remove("tac.txt");

remove("error.txt");
    printf(
        "Mini-C Compiler using Flex/Bison\n"
    );

    FILE *clear = fopen("error.txt", "w");

    fclose(clear);

    yyparse();
    if (root == NULL && !hasError) {

    FILE *fp = fopen("error.txt", "w");

    fprintf(fp, "Error: Empty input file\n");

    fclose(fp);

    printf("Error: Empty input file\n");

    hasError = 1;
}

    if (!hasError && root != NULL) {

    printf(
        "\nAnnotated Syntax Tree:\n\n"
    );

    printAST(root, 0);

    printSymbolTable();

    generateTAC(root);

    printTAC();
}

    FILE *fp = fopen("ast.dot", "w");

    fprintf(
        fp,
        "digraph AST {\n"
    );

    generateDOT(root, fp);

    fprintf(
        fp,
        "}\n"
    );

    fclose(fp);

    if (!hasError && root != NULL) {

        printf(
            "\nParsing Completed Successfully\n"
        );
    }
    else {

        remove("ast.png");

        remove("ast.dot");
        remove("tac.txt");

        printf(
            "\nCompilation Failed Due To Errors\n"
        );
    }

    return 0;
}