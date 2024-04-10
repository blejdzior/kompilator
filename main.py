from gen.asdLexer import *
from gen.asdParser import asdParser
from listener import Listener
from gen.asdListener import asdListener
from antlr4 import *
import os

def main():
    f = open("nasz.jezyk", "r")
    code = InputStream(f.read())
    lexer = asdLexer(input=code)
    tokens = CommonTokenStream(lexer)
    parser = asdParser(tokens)
    tree = parser.prog()
    listener = Listener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    
    os.system('clang-19 result.ll -o res')
    cwd = os.getcwd()
    os.system(cwd + "/res")


if __name__ == "__main__":
    main()
