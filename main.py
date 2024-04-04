from gen.asdLexer import *
from gen.asdParser import asdParser
from listener import Listener
from gen.asdListener import asdListener
from antlr4 import *


def main():
    code = InputStream("x = 10 print(x)")
    lexer = asdLexer(input=code)
    tokens = CommonTokenStream(lexer)
    parser = asdParser(tokens)
    tree = parser.prog()
    listener = Listener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)


if __name__ == "__main__":
    main()
