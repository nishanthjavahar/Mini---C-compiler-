%{

#include "ast.h"
#include "parser.tab.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

%}

%%

"int"           { return INT; }
"float"         { return FLOAT; }
"if"            { return IF; }
"else"          { return ELSE; }
"while"         { return WHILE; }
"print"         { return PRINT; }

[0-9]+          { yylval.num = atoi(yytext); return NUMBER; }

[a-zA-Z_][a-zA-Z0-9_]* {

                    yylval.str = strdup(yytext);

                    return ID;
                }

"+"             { return PLUS; }
"-"             { return MINUS; }
"*"             { return MUL; }
"/"             { return DIV; }

"="             { return ASSIGN; }

";"             { return SEMICOLON; }

"("             { return LPAREN; }
")"             { return RPAREN; }

"{"             { return LBRACE; }
"}"             { return RBRACE; }

"<"             { return LT; }
">"             { return GT; }
"<="    return LE;
">="    return GE;
"=="    return EQ;
"!="    return NE;
"["     return LBRACKET;
"]"     return RBRACKET;

[ \t\n]         ;

. {

    FILE *fp = fopen("error.txt", "w");

    fprintf(
        fp,
        "Lexical Error: Invalid character '%s'\n",
        yytext
    );

    fclose(fp);

    printf(
        "Lexical Error: Invalid character '%s'\n",
        yytext
    );
}

%%

int yywrap() {

    return 1;
}