compiler:
	bison -d parser.y
	flex lexer.l
	gcc parser.tab.c lex.yy.c ast.c symbol_table.c tac.c -o compiler
run:
	./compiler < test.mc

clean:
	rm -f compiler lex.yy.c parser.tab.c parser.tab.h