from gen.asdListener import asdListener
from gen.asdParser import asdParser
from LLVMgenerator import LLVMgenerator
from antlr4 import *

from enum import Enum
class VarType(Enum):
    INT = 1
    REAL = 2

class Value:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class Listener(asdListener):
    generator = LLVMgenerator()
    variables = []
    stack = []
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
        b = self.stack.pop()
        a = self.stack.pop()
        if a.type == b.type:
            if a.type == VarType.INT:
                self.generator.add_i32(a.name, b.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.INT) )

            if a.type == VarType.REAL:
                self.generator.add_double(a.name, b.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.REAL) )
        else:
            raise Exception(ctx.start.line, "add type mismatch")
        pass


    # Enter a parse tree produced by asdParser#assign.
    def enterAssign(self, ctx:asdParser.AssignContext):
        pass

    # Exit a parse tree produced by asdParser#assign.
    def exitAssign(self, ctx:asdParser.AssignContext):
        # declaring new variables
        ID = ctx.ID().symbol.text
        value = self.stack.pop()
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            self.variables.append((ID, value.type))
            if value.type == VarType.INT:
                self.generator.declare_i32(ID)
            elif value.type == VarType.REAL:
                self.generator.declare_double(ID)

        if value.type == VarType.INT:
            self.generator.assign_i32(ID, value.name)
        elif value.type == VarType.REAL:
            self.generator.assign_double(ID, value.name)


    def exitReal(self, ctx:asdParser.RealContext):
        self.stack.append(Value(ctx.REAL().symbol.text, VarType.REAL))

    def exitInt(self, ctx:asdParser.IntContext):
        self.stack.append(Value(ctx.INT().symbol.text, VarType.INT))

    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx:asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if ID == temp[0][0]:
            _type = temp[0][1]
            if _type == VarType.INT:
                self.generator.printf_i32(ID)
            elif _type == VarType.REAL:
                self.generator.printf_double(ID)
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
        v2 = self.stack.pop()
        v1 = self.stack.pop()
        if v1.type == v2.type:
            if v1.type == VarType.INT:
                self.generator.mult_i32(v1.name, v2.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.INT) )
            if v1.type == VarType.REAL:
                self.generator.mult_double(v1.name, v2.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.REAL) )

        else:
            raise Exception(ctx.start.line, "mult type mismatch")
        pass


    # Enter a parse tree produced by asdParser#div.
    def enterDiv(self, ctx:asdParser.DivContext):
        pass

    # Exit a parse tree produced by asdParser#div.
    def exitDiv(self, ctx:asdParser.DivContext):
        v2 = self.stack.pop()
        v1 = self.stack.pop()
        if float(v2.name) == 0:
            raise Exception(ctx.start.line, "divide by zero")

        if v1.type == v2.type:
            if v1.type == VarType.INT:
                self.generator.div_i32(v1.name, v2.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.INT) )
            if v1.type == VarType.REAL:
                self.generator.div_double(v1.name, v2.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.REAL) )

        else:
            raise Exception(ctx.start.line, "div type mismatch")
        pass


    # Enter a parse tree produced by asdParser#sub.
    def enterSub(self, ctx:asdParser.SubContext):
        pass

    # Exit a parse tree produced by asdParser#sub.
    def exitSub(self, ctx:asdParser.SubContext):
        b = self.stack.pop()
        a = self.stack.pop()
        if a.type == b.type:
            if a.type == VarType.INT:
                self.generator.sub_i32(a.name, b.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.INT) )

            if a.type == VarType.REAL:
                self.generator.sub_double(a.name, b.name)
                self.stack.append(Value("%"+str(self.generator.reg-1), VarType.REAL) )
        else:
            raise Exception(ctx.start.line, "sub type mismatch")
        pass


    # Enter a parse tree produced by asdParser#value.
    def enterValue(self, ctx:asdParser.ValueContext):
        pass

    # Exit a parse tree produced by asdParser#value.
    def exitValue(self, ctx:asdParser.ValueContext):
        pass


del asdParser