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

    os.system('clang result.ll -o res.exe')
    os.system("E:/Bartek/moje_PW/Magisterskie/1_sem_mgr/Jezyki-formalne-i-kompilatory/Lab/kompilator1/kompilator/res.exe")

if __name__ == "__main__":
    main()
