from gen.asdListener import asdListener
from gen.asdParser import asdParser
from LLVMgenerator import LLVMgenerator
from antlr4 import *


class Listener(asdListener):
    generator = LLVMgenerator()
    variables = []
    # Enter a parse tree produced by asdParser#prog.
    def enterProg(self, ctx:asdParser.ProgContext):
        pass

    # Exit a parse tree produced by asdParser#prog.
    def exitProg(self, ctx:asdParser.ProgContext):
        result = self.generator.generate()
        print(result)
        f = open("result.ll", "w")
        f.write(result)
        f.close()



    # Enter a parse tree produced by asdParser#add.
    def enterAdd(self, ctx:asdParser.AddContext):
        pass

    # Exit a parse tree produced by asdParser#add.
    def exitAdd(self, ctx:asdParser.AddContext):
        pass


    # Enter a parse tree produced by asdParser#assign.
    def enterAssign(self, ctx:asdParser.AssignContext):
        pass

    # Exit a parse tree produced by asdParser#assign.
    def exitAssign(self, ctx:asdParser.AssignContext):
        ID = ctx.ID().symbol.text
        INT = ctx.value().INT()
        if ID not in self.variables:
            self.variables.append(ID)
            self.generator.declare(ID)

        self.generator.assign(ID, INT)




    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx:asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        if ID in self.variables:
            self.generator.printf(ID)
        else:
            print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))


    # Enter a parse tree produced by asdParser#read.
    def enterRead(self, ctx:asdParser.ReadContext):
        pass

    # Exit a parse tree produced by asdParser#read.
    def exitRead(self, ctx:asdParser.ReadContext):
        ID = ctx.value().ID().symbol.text
        if ID not in self.variables:
            self.variables.append(ID)
            self.generator.declare(ID)
        self.generator.scanf(ID)



    # Enter a parse tree produced by asdParser#mult.
    def enterMult(self, ctx:asdParser.MultContext):
        pass

    # Exit a parse tree produced by asdParser#mult.
    def exitMult(self, ctx:asdParser.MultContext):
        pass


    # Enter a parse tree produced by asdParser#div.
    def enterDiv(self, ctx:asdParser.DivContext):
        pass

    # Exit a parse tree produced by asdParser#div.
    def exitDiv(self, ctx:asdParser.DivContext):
        pass


    # Enter a parse tree produced by asdParser#sub.
    def enterSub(self, ctx:asdParser.SubContext):
        pass

    # Exit a parse tree produced by asdParser#sub.
    def exitSub(self, ctx:asdParser.SubContext):
        pass


    # Enter a parse tree produced by asdParser#value.
    def enterValue(self, ctx:asdParser.ValueContext):
        pass

    # Exit a parse tree produced by asdParser#value.
    def exitValue(self, ctx:asdParser.ValueContext):
        pass


del asdParser