#include <stdio.h>
#include <string.h>

#include "symbol_table.h"

Symbol table[100];

int count = 0;

void addSymbol(char *name, char *type) {

    strcpy(table[count].name, name);

    strcpy(table[count].type, type);

    count++;
}

void printSymbolTable() {

    printf("\nSYMBOL TABLE\n");
    printf("-------------------------\n");

    printf("%-10s %-10s\n", "NAME", "TYPE");

    for (int i = 0; i < count; i++) {

        printf(
            "%-10s %-10s\n",
            table[i].name,
            table[i].type
        );
    }
}

int symbolExists(char *name) {

    for (int i = 0; i < count; i++) {

        if (strcmp(table[i].name, name) == 0) {

            return 1;
        }
    }

    return 0;
}
char* getType(char *name) {

    for (int i = 0; i < count; i++) {

        if (strcmp(table[i].name, name) == 0) {

            return table[i].type;
        }
    }

    return NULL;
}