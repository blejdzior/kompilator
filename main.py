from gen.asdLexer import *
from gen.asdParser import asdParser
from listener import Listener
from gen.asdListener import asdListener
from antlr4 import *

code = InputStream("function asd (x, y){ a=2 3*3 4*4 }")
lexer = asdLexer(input=code)
tokens = CommonTokenStream(lexer)
parser = asdParser(tokens)
tree = parser.prog()
listener = Listener()
walker = ParseTreeWalker()
walker.walk(listener, tree)

