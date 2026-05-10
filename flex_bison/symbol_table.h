#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

typedef struct {

    char name[50];

    char type[20];

} Symbol;

void addSymbol(char *name, char *type);

void printSymbolTable();

int symbolExists(char *name);

char* getType(char *name);

#endif