from gen.asdListener import asdListener
from gen.asdParser import asdParser
from LLVMgenerator import LLVMgenerator
from value import Value
from antlr4 import *
import numpy as np

from enum import Enum
class VarType(Enum):
    INT = 1
    REAL = 2
    BOOL = 3





class Listener(asdListener):
    def __init__(self):
        self.generator = LLVMgenerator()
        self.variables = []
        self.stack = []
        self.int = ['i8', 'i16', 'i32', 'i64']
        self.float = ['f32', 'f64']

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
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
        except AttributeError:
            type = None
        
        # Can assign var to var if: try: value = self.stack.pop() except IndexError: value = ctx.value().ID().symbol.text
        value = self.stack.pop()

        temp = [(x, y) for x, y in self.variables if x == ID]

        # if ID is not in self.variables
        if len(temp) == 0:
            # check if declared type matches value type
            if type in self.int and value.type == VarType.INT:
                bitlen = int(value.name).bit_length()
                if type == self.int[0] and bitlen in range (8): # i8
                    self.generator.declare_i8(ID)
                elif type == self.int[1] and bitlen in range(16): # i16
                    self.generator.declare_i16(ID)
                elif type == self.int[2] and bitlen in range(32): # i32      
                    self.generator.declare_i32(ID)
                elif type == self.int[3] and bitlen in range(64): # i64
                    self.generator.declare_i64(ID)
                else:
                    print("Line: " + str(ctx.start.line) + ", integer number is too large to write to " + str(type))
                    return
            elif type in self.float and value.type == VarType.REAL:
                if type == self.float[0]: # f32
                    self.generator.declare_float32(ID) 
                elif type == self.float[1]: # f64
                    self.generator.declare_double(ID)
            elif type == 'bool' or value.type == VarType.BOOL:
                self.generator.declare_bool(ID)
            elif type == None: # no declared type
                if value.type == VarType.INT:
                    self.generator.declare_i32(ID)
                elif value.type == VarType.REAL:
                    self.generator.declare_double(ID)  
          
            else:
                print("Line: " + str(ctx.start.line) + ", VarType and ValueType mismatch")
                return

            if type:
                self.variables.append((ID, type))
            else:
                self.variables.append((ID, value.type))
        
        # if no declared type then get type of value
        if type == None:
            type = value.type

        if type == VarType.INT:
            self.generator.assign_i32(ID, value.name)
        elif type == VarType.REAL:
            self.generator.assign_double(ID, value.name)
        elif type == 'bool' or type == VarType.BOOL:
            if value.name == 'true':
                self.generator.assign_bool(ID, 1)
            elif value.name == 'false':
                self.generator.assign_bool(ID, 0)
            else:
                self.generator.assign_bool(ID, value.name)
        elif type in self.int:
            if type == 'i8':
                self.generator.assign_i8(ID, value.name)
            elif type == 'i16':
                self.generator.assign_i16(ID, value.name)
            elif type == 'i32':
                self.generator.assign_i32(ID, value.name)
            elif type == 'i64':
                self.generator.assign_i64(ID, value.name)
        elif type in self.float:
            if type == 'f32':
                self.generator.assign_float32(ID, value.name)
            elif type == 'f64':
                self.generator.assign_double(ID, value.name)


    def exitReal(self, ctx:asdParser.RealContext):
        self.stack.append(Value(ctx.REAL().symbol.text, VarType.REAL))

    def exitInt(self, ctx:asdParser.IntContext):
        self.stack.append(Value(ctx.INT().symbol.text, VarType.INT))
    def exitBool(self, ctx:asdParser.BoolContext):
        self.stack.append(Value(ctx.BOOL().symbol.text, VarType.BOOL))

    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx:asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            _type = temp[0][1]
            if _type == VarType.INT:
                self.generator.printf_i32(ID)
            elif _type == VarType.REAL:
                self.generator.printf_double(ID)
            elif _type == 'bool' or _type == VarType.BOOL:
                self.generator.printf_bool(ID)
            elif _type in self.int:
                if _type == 'i8':
                    self.generator.printf_i8(ID)
                elif _type == 'i16':
                    self.generator.printf_i16(ID)
                elif _type == 'i32':
                    self.generator.printf_i32(ID)
                elif _type == 'i64':
                    self.generator.printf_i64(ID)
            elif _type in self.float:
                if _type == 'f32':
                    self.generator.printf_float32(ID)
                elif _type == 'f64':
                    self.generator.printf_double(ID)
            else:
                print("Line: " + str(ctx.start.line) + ", unknown variable type")
        else:
            print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))


    # Enter a parse tree produced by asdParser#read.
    def enterRead(self, ctx:asdParser.ReadContext):
        pass

    # Exit a parse tree produced by asdParser#read.
    def exitRead(self, ctx:asdParser.ReadContext):
        ID = ctx.ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))
            return
        _type = temp[0][1]
        if _type == VarType.INT:
            self.generator.scanf_int32(ID)
        elif _type == VarType.REAL:
            self.generator.scanf_double(ID)
        elif _type == 'bool' or _type == VarType.BOOL:
            self.generator.scanf_bool(ID)
        elif _type in self.int:
            if _type == 'i8':
                self.generator.scanf_int8(ID)
            elif _type == 'i16':
                self.generator.scanf_int16(ID)
            elif _type == 'i32':
                self.generator.scanf_int32(ID)
            elif _type == 'i64':
                self.generator.scanf_int64(ID)
        elif _type in self.float:
            if _type == 'f32':
                self.generator.scanf_float32(ID)
            elif _type == 'f64':
                self.generator.scanf_double(ID)
        else:
            print("Line: " + str(ctx.start.line) + ", unknown variable type")
        
    def exitAndOp(self, ctx:asdParser.AndOpContext):
        try:
            v1 = ctx.value(0).ID().symbol.text
        except AttributeError:
            try:
                v1 = self.stack.pop()
            except IndexError:
                v1 = ctx.value(0).BOOL().symbol.text
        
        try:
            v2 = ctx.value(1).ID().symbol.text
        except AttributeError:
            try:
                v2 = self.stack.pop()
            except IndexError:
                v2 = ctx.value(1).BOOL().symbol.text
  
        self.generator.andOp(v1, v2)
        self.stack.append(Value("%"+str(self.generator.reg-1), VarType.BOOL))

    # def enterOrOp(self, ctx:asdParser.OrOpContext):
    #     try:
    #         v1 = ctx.value(0).ID().symbol.text
    #     except AttributeError:
    #         try:
    #             v1 = self.stack.pop()
    #         except IndexError:
    #             v1 = ctx.value(0).BOOL().symbol.text
        
    #     try:
    #         v2 = ctx.value(1).ID().symbol.text
    #     except AttributeError:
    #         try:
    #             v2 = self.stack.pop()
    #         except IndexError:
    #             v2 = ctx.value(1).BOOL().symbol.text
    #         except:
    #             print("dddddddddddd")

    def exitNegOp(self, ctx:asdParser.NegOpContext):
        try:
            v = ctx.value().ID().symbol.text
        except AttributeError:
            try:
                v = self.stack.pop()
            except IndexError():
                v = ctx.value().BOOL().symbol.text
        
        self.generator.NegOp(v)
        self.stack.append(Value("%"+str(self.generator.reg-1), VarType.BOOL))


    def exitOrOp(self, ctx:asdParser.OrOpContext):
        try:
            v1 = ctx.value(0).ID().symbol.text
        except AttributeError:
            try:
                v1 = self.stack.pop()
            except IndexError:
                v1 = ctx.value(0).BOOL().symbol.text
        
        try:
            v2 = ctx.value(1).ID().symbol.text
        except AttributeError:
            try:
                v2 = self.stack.pop()
            except IndexError:
                v2 = ctx.value(1).BOOL().symbol.text
  
        self.generator.orOp(v1, v2)
        self.stack.append(Value("%"+str(self.generator.reg-1), VarType.BOOL))
    
    def exitXorOp(self, ctx:asdParser.XorOpContext):
        try:
            v1 = ctx.value(0).ID().symbol.text
        except AttributeError:
            try:
                v1 = self.stack.pop()
            except IndexError:
                v1 = ctx.value(0).BOOL().symbol.text
        
        try:
            v2 = ctx.value(1).ID().symbol.text
        except AttributeError:
            try:
                v2 = self.stack.pop()
            except IndexError:
                v2 = ctx.value(1).BOOL().symbol.text
  
        self.generator.XorOp(v1, v2)
        self.stack.append(Value("%"+str(self.generator.reg-1), VarType.BOOL))

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