from gen.asdListener import asdListener
from gen.asdParser import asdParser
from antlr4 import *


class Listener(asdListener):

    def __init__(self):
        declarations = []

    # Enter a parse tree produced by asdParser#prog.
    def enterProg(self, ctx:asdParser.ProgContext):
        print("enter prog")

    # Exit a parse tree produced by asdParser#prog.
    def exitProg(self, ctx: asdParser.ProgContext):
        pass

    # Enter a parse tree produced by asdParser#expr.
    def enterExpr(self, ctx: asdParser.ExprContext):
        pass

    # Exit a parse tree produced by asdParser#expr.
    def exitExpr(self, ctx: asdParser.ExprContext):
        pass

    # Enter a parse tree produced by asdParser#function.
    def enterFunction(self, ctx: asdParser.FunctionContext):
        pass

    # Exit a parse tree produced by asdParser#function.
    def exitFunction(self, ctx: asdParser.FunctionContext):
        pass

    # Enter a parse tree produced by asdParser#compoundStat.
    def enterCompoundStat(self, ctx: asdParser.CompoundStatContext):
        pass

    # Exit a parse tree produced by asdParser#compoundStat.
    def exitCompoundStat(self, ctx: asdParser.CompoundStatContext):
        pass

    # Enter a parse tree produced by asdParser#value.
    def enterValue(self, ctx: asdParser.ValueContext):
        pass

    # Exit a parse tree produced by asdParser#value.
    def exitValue(self, ctx: asdParser.ValueContext):
        pass

del asdParser