from gen.asdListener import asdListener
from gen.asdParser import asdParser
from LLVMgenerator import LLVMgenerator
from value import Value
from antlr4 import *
import numpy as np

from enum import Enum
class VarType(Enum):
    INT8 = 1
    INT16 = 2
    INT32 = 3
    INT64 = 4
    REAL32 = 5
    REAL64 = 6
    BOOL = 7





class Listener(asdListener):
    def __init__(self):
        self.generator = LLVMgenerator()
        self.variables = []
        self.stack = []
        self.int = ['i8', 'i16', 'i32', 'i64']
        self.float = ['f32', 'f64']
        self.ints = [VarType.INT8, VarType.INT16, VarType.INT32, VarType.INT64]
        self.floats = [VarType.REAL32, VarType.REAL64]

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

        if a.type == VarType.BOOL or b.type == VarType.BOOL:
            raise Exception(ctx.start.line, "Bool is not addable")

        if (a.type in self.floats) != (b.type in self.floats):
            if a.type in self.ints:
                self.generator.int_to_real(a.name, self.getTypeStr(a.type), 'double')
                a.name = '%' + str(self.generator.reg - 1)
                a.type = VarType.REAL64
            elif b.type in self.ints:
                self.generator.int_to_real(b.name, self.getTypeStr(b.type), 'double')
                b.type = VarType.REAL64
                b.name = '%' + str(self.generator.reg - 1)


        if a.type != VarType.INT64 and a.type != VarType.REAL64:
            if a.type.value < VarType.INT64.value:
                self.generator.increase_type(a.name, self.getTypeStr(a.type), 'i64')
                a.type = VarType.INT64
            else:
                self.generator.increase_type(a.name, self.getTypeStr(a.type), 'double')
                a.type = VarType.REAL64

            a.name = '%' + str(self.generator.reg-1)

        if b.type != VarType.INT64 and b.type != VarType.REAL64:
            if b.type.value < VarType.INT64.value:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'i64')
                b.type = VarType.INT64
            else:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'double')
                b.type = VarType.REAL64

            b.name = '%' + str(self.generator.reg - 1)

        if a.type == VarType.INT64:
            self.generator.add_i64(a.name, b.name)
            self.stack.append(Value("%"+str(self.generator.reg-1), VarType.INT64) )
            self.variables.append((str(self.generator.reg-1), VarType.INT64))

        if a.type == VarType.REAL64:
            self.generator.add_double(a.name, b.name)
            self.stack.append(Value("%"+str(self.generator.reg-1), VarType.REAL64) )
            self.variables.append((str(self.generator.reg - 1), VarType.REAL64))


    # Enter a parse tree produced by asdParser#assign.
    def enterAssign(self, ctx:asdParser.AssignContext):
        pass

    # Exit a parse tree produced by asdParser#assign.
    def exitAssign(self, ctx:asdParser.AssignContext):
        # declaring new variables
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
            if type == 'i8':
                type = VarType.INT8
            elif type == 'i16':
                type = VarType.INT16
            elif type == 'i32':
                type = VarType.INT32
            elif type == 'i64':
                type = VarType.INT64
            elif type == 'f32':
                type = VarType.REAL32
            elif type == 'f64':
                type = VarType.REAL64
        except AttributeError:
            type = None
        
        # Can assign var to var if: try: value = self.stack.pop() except IndexError: value = ctx.value().ID().symbol.text
        value = self.stack.pop()

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            type = temp[0][1]

        # if no declared type then get type of value
        if type == None:
            type = value.type

        # if ID is not in self.variables
        if len(temp) == 0:
            # check if declared type matches value type
            if type in self.ints and value.type in self.ints:
                print(value, value.name)
                bitlen = int(value.name).bit_length()
                if type == VarType.INT8 and bitlen in range (8): # i8
                    self.generator.declare_i8(ID)
                elif type == VarType.INT16 and bitlen in range(16): # i16
                    self.generator.declare_i16(ID)
                elif type == VarType.INT32 and bitlen in range(32): # i32
                    self.generator.declare_i32(ID)
                elif type == VarType.INT64 and bitlen in range(64): # i64
                    self.generator.declare_i64(ID)
                else:
                    print("Line: " + str(ctx.start.line) + ", integer number is too large to write to " + str(type))
                    return
            elif type in self.floats and value.type in self.floats:
                if type == VarType.REAL32: # f32
                    self.generator.declare_float32(ID)
                elif type == VarType.REAL64: # f64
                    self.generator.declare_double(ID)
            elif type == 'bool' or value.type == VarType.BOOL:
                self.generator.declare_bool(ID)
            elif type == None: # no declared type
                if value.type == VarType.INT32:
                    self.generator.declare_i32(ID)
                elif value.type == VarType.REAL64:
                    self.generator.declare_double(ID)

            else:
                print("Line: " + str(ctx.start.line) + ", VarType and ValueType mismatch", type, value.type)
                return

            if type:
                self.variables.append((ID, type))
            else:
                self.variables.append((ID, value.type))


        if value.name[0] == '%' and type != value.type:
            if type in self.ints and value.type in self.floats:
                self.generator.real_to_int("%"+str(self.generator.reg-1), self.getTypeStr(value.type), self.getTypeStr(type))
            elif type in self.floats and value.type in self.ints:
                self.generator.int_to_real("%"+str(self.generator.reg-1), self.getTypeStr(value.type), self.getTypeStr(type))
            elif type == VarType.REAL32 and value.type == VarType.REAL64:
                self.generator.double_to_float("%"+str(self.generator.reg-1))
            elif type.value > value.type.value:
                self.generator.increase_type("%"+str(self.generator.reg-1), self.getTypeStr(value.type), self.getTypeStr(type))
            elif type.value < value.type.value:
                self.generator.decrease_type("%"+str(self.generator.reg-1), self.getTypeStr(value.type), self.getTypeStr(type))

            value.name = "%"+str(self.generator.reg-1)



        if type == VarType.INT8:
            self.generator.assign_i8(ID, value.name)
        elif type == VarType.INT16:
            self.generator.assign_i16(ID, value.name)
        elif type == VarType.INT32:
            self.generator.assign_i32(ID, value.name)
        elif type == VarType.INT64:
            self.generator.assign_i64(ID, value.name)
        elif type == VarType.REAL32:
            self.generator.assign_float32(ID, value.name)
        elif type == VarType.REAL64:
            self.generator.assign_double(ID, value.name)
        elif type == 'bool' or type == VarType.BOOL:
            if value.name == 'true':
                self.generator.assign_bool(ID, 1)
            elif value.name == 'false':
                self.generator.assign_bool(ID, 0)
            else:
                self.generator.assign_bool(ID, value.name)



    def exitReal(self, ctx:asdParser.RealContext):
        self.stack.append(Value(ctx.REAL().symbol.text, VarType.REAL64))

    def exitInt(self, ctx:asdParser.IntContext):
        self.stack.append(Value(ctx.INT().symbol.text, VarType.INT64))

    def exitBool(self, ctx:asdParser.BoolContext):
        self.stack.append(Value(ctx.BOOL().symbol.text, VarType.BOOL))

    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx:asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            _type = temp[0][1]
            if _type == VarType.INT8:
                self.generator.printf_i8(ID)
            elif _type == VarType.INT16:
                self.generator.printf_i16(ID)
            elif _type == VarType.INT32:
                self.generator.printf_i32(ID)
            elif _type == VarType.INT64:
                self.generator.printf_i64(ID)
            elif _type == VarType.REAL32:
                self.generator.printf_float32(ID)
            elif _type == VarType.REAL64:
                self.generator.printf_double(ID)
            elif _type == 'bool' or _type == VarType.BOOL:
                self.generator.printf_bool(ID)
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

    # Enter a parse tree produced by asdParser#id.
    def enterId(self, ctx:asdParser.IdContext):
        pass

    def getTypeStr(self, varTp):
        if varTp == VarType.INT8:
            return 'i8'
        elif varTp == VarType.INT16:
            return 'i16'
        elif varTp == VarType.INT32:
            return 'i32'
        elif varTp == VarType.INT64:
            return 'i64'
        elif varTp == VarType.REAL32:
            return 'float'
        elif varTp == VarType.REAL64:
            return 'double'


    # Exit a parse tree produced by asdParser#id.
    def exitId(self, ctx:asdParser.IdContext):
        ID = str(ctx.ID())

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            raise Exception(ctx.start.line, "undeclared variable: ", ID)
        else:
            type = self.getTypeStr(temp[0][1])
            self.generator.load("%" + str(ctx.ID()), type)
            self.stack.append(Value("%" + str(self.generator.reg-1), temp[0][1]))

        pass

del asdParser