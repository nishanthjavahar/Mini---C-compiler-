// ============================================
// error_test.mc
// This file has intentional errors to show
// what the compiler's error messages look like
// ============================================

int x = 5;
int x = 10;          // ERROR: redeclaration of x

float y = 3.14;
int z = y;           // ERROR: type mismatch (float -> int)

print(undeclared);   // ERROR: undeclared variable

int @ = 5;           // ERROR: invalid character @
