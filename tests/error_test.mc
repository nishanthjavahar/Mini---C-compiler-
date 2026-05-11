(.venv) admin@MacBookPro flex_bison % ./compiler < ../tests/test_program.mc
Mini-C Compiler using Flex/Bison
Declaration: int a
Assignment Parsed
Semantic Error: Variable 'b' not declared

Annotated Syntax Tree:

├── =
│   ├── a
│   ├── 10

SYMBOL TABLE
-------------------------
NAME       TYPE      
a          int       

THREE ADDRESS CODE
-------------------------
a = 10

Compilation Failed Due To Errors