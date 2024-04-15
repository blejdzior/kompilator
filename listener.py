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
    STRING = 8
    ARRAY = 9
    MATRIX = 10


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
    def enterProg(self, ctx: asdParser.ProgContext):
        pass

    # Exit a parse tree produced by asdParser#prog.
    def exitProg(self, ctx: asdParser.ProgContext):
        result = self.generator.generate()
        print(result)
        f = open("result.ll", "w")
        f.write(result)
        f.close()


    # Exit a parse tree produced by asdParser#add.
    def exitAdd(self, ctx: asdParser.AddContext):
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

            a.name = '%' + str(self.generator.reg - 1)

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
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.INT64))
            self.variables.append((str(self.generator.reg - 1), VarType.INT64))

        if a.type == VarType.REAL64:
            self.generator.add_double(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.REAL64))
            self.variables.append((str(self.generator.reg - 1), VarType.REAL64))

    def exitMatrixAccess(self, ctx: asdParser.MatrixAccessContext):
        ID = ctx.ID().symbol.text
        indexes = (ctx.INT(0).symbol.text, ctx.INT(1).symbol.text)
        temp = [(x, y) for x, y in self.variables if x == ID]
        matrix_type, type, rows, cols = temp[0][1]
        if int(indexes[0]) >= rows or int(indexes[1]) >= cols:
            print(f"Line: {ctx.start.line}, index out of range")
            return
        if len(temp) == 0 or matrix_type != VarType.MATRIX:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return      
             
        self.generator.matrix_access(ID, indexes, type=type, rows=rows, cols=cols)

        type = self.string_to_type(type)

        self.stack.append(Value("%" + str(self.generator.reg - 1), type))


    def exitArrayAccess(self, ctx: asdParser.ArrayAccessContext):
        ID = ctx.ID().symbol.text
        index = ctx.INT().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        arr_type, type, size = temp[0][1]
        if int(index) >= size:
            print(f"Line: {ctx.start.line}, index out of range")
            return

        if len(temp) == 0 or arr_type != VarType.ARRAY:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return
    
        self.generator.array_access(ID, index, type=type, size=size)

        type = self.string_to_type(type)

        self.stack.append(Value("%" + str(self.generator.reg - 1), type))

    def exitElementAssign(self, ctx: asdParser.ElementAssignContext):
        ID = ctx.ID().symbol.text
        index = ctx.INT().symbol.text

        temp = [(x, y) for x, y in self.variables if x == ID]
        arr_type, type, size = temp[0][1]
        if int(index) >= size:
            print(f"Line: {ctx.start.line}, index out of range")
            return
        if len(temp) == 0 or arr_type != VarType.ARRAY:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return

        value = self.stack.pop()
        self.generator.element_assign(ID, index, value.name, type=type, size=size)

    def exitMatrixAssign(self, ctx: asdParser.MatrixAssignContext):
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
            print(type)
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            if type  != temp[0][1][1]:
                type = temp[0][1][1]
                type = self.string_to_type(type)

        matrix = self.stack.pop()
        if matrix.type != VarType.MATRIX:
            print("Line: " + str(ctx.start.line) + "Variable not of type matrix") 
            return
        
        if matrix.name == 0:
            print("Line: " + str(ctx.start.line) + ", matrix cannot be initialized without values")
            return

        if type == None:
            try:
                type = self.stack[-2].type
            except IndexError:
                print(f"Line: {ctx.start.line}, array cannot be initialized without values")
                return
        if type == VarType.STRING:
            print(f"Line: {ctx.start.line}, array cannot be initialized with string")
            return        
        rows = matrix.name # number of matrix lines
        cols = self.stack[-1].name # number of elements of first line in matrix
        lines = []
        for i in range(rows):
            arr = self.stack.pop()
            if arr.name != cols:
                print(f"Line: {ctx.start.line}, all rows must have the same number of elements")
                return
            values = [] 
            for j in range(arr.name): #for assignment arr.name holds number of elements in array
                v = self.stack.pop()
                if v.type != type:
                    print(f"Line: {ctx.start.line}, all values in array must be of same type {type} but found {v.type}")
                    exit()
                values.append(v.name)
            values.reverse()
            lines.append(values)
        lines.reverse()
        
        type = self.type_to_string(type)

        if len(temp) == 0:
            self.generator.declare_matrix(ID, type = type, rows = rows, cols = cols)
            self.variables.append((ID, (matrix.type, type, rows, cols)))
        
        self.generator.assign_matrix(ID, type = type, rows = rows, cols = cols, lines = lines)




    def exitArrayAssign(self, ctx: asdParser.ArrayAssignContext):
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
            print(type)
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            if type  != temp[0][1][1]:
                type = temp[0][1][1]
                type = self.string_to_type(type)


        arr = self.stack.pop()
        if arr.type != VarType.ARRAY:
            print("Line: " + str(ctx.start.line) + "Variable not of type array") 
        
        if arr.name == 0:
            print("Line: " + str(ctx.start.line) + ", array cannot be initialized without values")
            return

        if type == None:
            try:
                type = self.stack[-1].type
            except IndexError:
                print(f"Line: {ctx.start.line}, array cannot be initialized without values")
                return
        if type == VarType.STRING:
            print(f"Line: {ctx.start.line}, array cannot be initialized with string")
            return        
        
        # get all values in array
        values = []
        for i in range(arr.name): #for assignment arr.name holds number of elements in array
            v = self.stack.pop()
            if v.type != type:
                print(f"Line: {ctx.start.line}, all values in array must be of same type {type} but found {v.type}")
                exit()
            values.append(v.name)
        values.reverse()

        type = self.type_to_string(type)

        if len(temp) == 0:
            self.generator.declare_array(ID, type = type, size = arr.name)
            self.variables.append((ID, (arr.type, type, arr.name)))
        
        self.generator.assign_array(ID, type = type, size = arr.name, values = values)


    # Exit a parse tree produced by asdParser#assign.
    def exitAssign(self, ctx: asdParser.AssignContext):
        # declaring new variables
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
            print(type)
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None

        # Can assign var to var if: try: value = self.stack.pop() except IndexError: value = ctx.value().ID().symbol.text
        value = self.stack.pop()

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            type = temp[0][1]

        print(123, type)
        # if no declared type then get type of value
        if type == None:
            type = value.type


        # if ID is not in self.variables
        if len(temp) == 0:
            # check if declared type matches value type
            if type in self.ints and value.type in self.ints:
                print(value, value.name)
                bitlen = int(value.name).bit_length()
                if type == VarType.INT8 and bitlen in range(8):  # i8
                    self.generator.declare_i8(ID)
                elif type == VarType.INT16 and bitlen in range(16):  # i16
                    self.generator.declare_i16(ID)
                elif type == VarType.INT32 and bitlen in range(32):  # i32
                    self.generator.declare_i32(ID)
                elif type == VarType.INT64 and bitlen in range(64):  # i64
                    self.generator.declare_i64(ID)
                else:
                    print("Line: " + str(ctx.start.line) + ", integer number is too large to write to " + str(type))
                    return
            elif type in self.floats and value.type in self.floats:
                if type == VarType.REAL32:  # f32
                    self.generator.declare_float32(ID)
                elif type == VarType.REAL64:  # f64
                    self.generator.declare_double(ID)
            elif type == 'bool' or type == VarType.BOOL or value.type == VarType.BOOL:
                self.generator.declare_bool(ID)
            elif type == VarType.STRING:
                self.generator.declare_string(ID)
            elif type == None:  # no declared type
                if value.type == VarType.INT32:
                    self.generator.declare_i32(ID)
                elif value.type == VarType.REAL64:
                    self.generator.declare_double(ID)
                elif value.type == VarType.STRING:
                    self.generator.declare_string(ID)

            else:
                print("Line: " + str(ctx.start.line) + ", VarType and ValueType mismatch", type, value.type)
                return

            if type:
                self.variables.append((ID, type))
            else:
                self.variables.append((ID, value.type))

        if value.name[0] == '%' and type != value.type:
            if type in self.ints and value.type in self.floats:
                self.generator.real_to_int("%" + str(self.generator.reg - 1), self.getTypeStr(value.type),
                                           self.getTypeStr(type))
            elif type in self.floats and value.type in self.ints:
                self.generator.int_to_real("%" + str(self.generator.reg - 1), self.getTypeStr(value.type),
                                           self.getTypeStr(type))
            elif type == VarType.REAL32 and value.type == VarType.REAL64:
                self.generator.double_to_float("%" + str(self.generator.reg - 1))
            elif type.value > value.type.value:
                self.generator.increase_type("%" + str(self.generator.reg - 1), self.getTypeStr(value.type),
                                             self.getTypeStr(type))
            elif type.value < value.type.value:
                self.generator.decrease_type("%" + str(self.generator.reg - 1), self.getTypeStr(value.type),
                                             self.getTypeStr(type))

            value.name = "%" + str(self.generator.reg - 1)

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
        elif type == VarType.STRING:
            self.generator.assign_string(ID, value.name)


    def exitReal(self, ctx: asdParser.RealContext):
        self.stack.append(Value(ctx.REAL().symbol.text, VarType.REAL64))

    def exitInt(self, ctx: asdParser.IntContext):
        self.stack.append(Value(ctx.INT().symbol.text, VarType.INT64))

    def exitBool(self, ctx: asdParser.BoolContext):
        self.stack.append(Value(ctx.BOOL().symbol.text, VarType.BOOL))

    def exitString(self, ctx: asdParser.StringContext):
        self.stack.append(Value(ctx.STRING().symbol.text, VarType.STRING) )
        tmp = ctx.STRING().getText()
        content = tmp[1:-1]
        self.generator.constant_string(content)
        n = "ptrstr"+str(self.generator.str-1)
        self.stack.append(Value(n, VarType.STRING))
    
    def exitArray(self, ctx: asdParser.ArrayContext):
        i = 0
        for value in ctx.value():
            i += 1

        self.stack.append(Value(i, VarType.ARRAY))

    def exitMatrixLine(self, ctx: asdParser.MatrixLineContext):
        i = 0
        for value in ctx.value():
            i += 1
        self.stack.append(Value(i ,VarType.ARRAY))
    
    def exitMatrix(self, ctx: asdParser.MatrixContext):
        i = 0
        for value in ctx.matLine():
            i += 1
        self.stack.append(Value(i, VarType.MATRIX))
    
    def string_to_type(self, string):
        if string == "i8":
            return VarType.INT8
        elif string == "i16":
            return VarType.INT16
        elif string == "i32":
            return VarType.INT32
        elif string == "i64":
            return VarType.INT64
        elif string == "float":
            return VarType.REAL32
        elif string == "double":
            return VarType.REAL64
        elif string == 'bool' or string == VarType.BOOL:
            return VarType.BOOL
        else:
            return string



    def type_to_string(self, type):
        if type == VarType.INT8:
            return "i8"
        elif type == VarType.INT16:
            return "i16"
        elif type == VarType.INT32:
            return "i32"
        elif type == VarType.INT64:
            return 'i64'
        elif type == VarType.REAL32:
            return "float"
        elif type == VarType.REAL64:
            return "double"
        elif type == 'bool' or type == VarType.BOOL:
            return "i1"

        

    
    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx: asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
    
        if len(temp) != 0:
            _type = temp[0][1]
            try:
                if _type[0] == VarType.ARRAY:
                    v = self.stack.pop()
                    ID = v.name[1:]
                    _type = v.type
                    __type = self.type_to_string(_type)
                    # have to transform variable created by generator.arrayAccess to ptr type
                    self.generator.printf_array_element(ID, __type)
                    ID = str(self.generator.reg - 1)
                elif _type[0] == VarType.MATRIX:
                    v = self.stack.pop()
                    ID = v.name[1:]
                    _type = v.type
                    __type = self.type_to_string(_type)
                    self.generator.printf_array_element(ID, __type)
                    ID = str(self.generator.reg - 1)
            except:
                pass
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

            elif _type == VarType.STRING:
                print("print string")
                self.generator.printf_string(ID)
            else:
                print("Line: " + str(ctx.start.line) + ", unknown variable type")
        else:
            print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))

    # Enter a parse tree produced by asdParser#read.
    def enterRead(self, ctx: asdParser.ReadContext):
        pass

    # Exit a parse tree produced by asdParser#read.
    def exitRead(self, ctx: asdParser.ReadContext):
        ID = ctx.ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))
            return
        _type = temp[0][1]
        if _type == VarType.INT8:
            self.generator.scanf_int8(ID)
        elif _type == VarType.INT16:
            self.generator.scanf_int16(ID)
        elif _type == VarType.INT32:
            self.generator.scanf_int32(ID)
        elif _type == VarType.INT64:
            self.generator.scanf_int64(ID)
        elif _type == VarType.REAL32:
            self.generator.scanf_float32(ID)
        elif _type == VarType.REAL64:
            self.generator.scanf_double(ID)
        elif _type == 'bool' or _type == VarType.BOOL:
            self.generator.scanf_bool(ID)
        elif _type == VarType.STRING:
            self.generator.scanf_string(ID)
        else:
            print("Line: " + str(ctx.start.line) + ", unknown variable type")

    def exitAndOp(self, ctx: asdParser.AndOpContext):
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
        self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.BOOL))

    def exitNegOp(self, ctx: asdParser.NegOpContext):
        try:
            v = ctx.value().ID().symbol.text
        except AttributeError:
            try:
                v = self.stack.pop()
            except IndexError():
                v = ctx.value().BOOL().symbol.text

        self.generator.NegOp(v)
        self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.BOOL))

    def exitOrOp(self, ctx: asdParser.OrOpContext):
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
        self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.BOOL))

    def exitXorOp(self, ctx: asdParser.XorOpContext):
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
        self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.BOOL))

    # Enter a parse tree produced by asdParser#mult.
    def enterMult(self, ctx: asdParser.MultContext):
        pass

    # Exit a parse tree produced by asdParser#mult.
    def exitMult(self, ctx: asdParser.MultContext):
        b = self.stack.pop()
        a = self.stack.pop()

        if a.type == VarType.BOOL or b.type == VarType.BOOL:
            raise Exception(ctx.start.line, "Bool is not multiplicatable")

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

            a.name = '%' + str(self.generator.reg - 1)

        if b.type != VarType.INT64 and b.type != VarType.REAL64:
            if b.type.value < VarType.INT64.value:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'i64')
                b.type = VarType.INT64
            else:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'double')
                b.type = VarType.REAL64

            b.name = '%' + str(self.generator.reg - 1)

        if a.type == VarType.INT64:
            self.generator.mult_i64(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.INT64))
            self.variables.append((str(self.generator.reg - 1), VarType.INT64))

        if a.type == VarType.REAL64:
            self.generator.mult_double(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.REAL64))
            self.variables.append((str(self.generator.reg - 1), VarType.REAL64))

    # Enter a parse tree produced by asdParser#div.
    def enterDiv(self, ctx: asdParser.DivContext):
        pass

    # Exit a parse tree produced by asdParser#div.
    def exitDiv(self, ctx: asdParser.DivContext):
        b = self.stack.pop()
        a = self.stack.pop()

        # if float(b.name) == 0:
        #     raise Exception(ctx.start.line, "divide by zero")

        if a.type == VarType.BOOL or b.type == VarType.BOOL:
            raise Exception(ctx.start.line, "Bool is not dividable")

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

            a.name = '%' + str(self.generator.reg - 1)

        if b.type != VarType.INT64 and b.type != VarType.REAL64:
            if b.type.value < VarType.INT64.value:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'i64')
                b.type = VarType.INT64
            else:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'double')
                b.type = VarType.REAL64

            b.name = '%' + str(self.generator.reg - 1)

        if a.type == VarType.INT64:
            self.generator.div_i64(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.INT64))
            self.variables.append((str(self.generator.reg - 1), VarType.INT64))

        if a.type == VarType.REAL64:
            self.generator.div_double(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.REAL64))
            self.variables.append((str(self.generator.reg - 1), VarType.REAL64))

    # Enter a parse tree produced by asdParser#sub.
    def enterSub(self, ctx: asdParser.SubContext):
        pass

    # Exit a parse tree produced by asdParser#sub.
    def exitSub(self, ctx: asdParser.SubContext):
        b = self.stack.pop()
        a = self.stack.pop()

        if a.type == VarType.BOOL or b.type == VarType.BOOL:
            raise Exception(ctx.start.line, "Bool is not subtractable")

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

            a.name = '%' + str(self.generator.reg - 1)

        if b.type != VarType.INT64 and b.type != VarType.REAL64:
            if b.type.value < VarType.INT64.value:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'i64')
                b.type = VarType.INT64
            else:
                self.generator.increase_type(b.name, self.getTypeStr(b.type), 'double')
                b.type = VarType.REAL64

            b.name = '%' + str(self.generator.reg - 1)

        if a.type == VarType.INT64:
            self.generator.sub_i64(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.INT64))
            self.variables.append((str(self.generator.reg - 1), VarType.INT64))

        if a.type == VarType.REAL64:
            self.generator.sub_double(a.name, b.name)
            self.stack.append(Value("%" + str(self.generator.reg - 1), VarType.REAL64))
            self.variables.append((str(self.generator.reg - 1), VarType.REAL64))

    # Enter a parse tree produced by asdParser#value.
    def enterValue(self, ctx: asdParser.ValueContext):
        pass

    # Exit a parse tree produced by asdParser#value.
    def exitValue(self, ctx: asdParser.ValueContext):
        pass

    # Enter a parse tree produced by asdParser#id.
    def enterId(self, ctx: asdParser.IdContext):
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
        elif varTp == VarType.BOOL:
            return 'i1'
        elif varTp == VarType.STRING:
            return 'i8*'

    # Exit a parse tree produced by asdParser#id.
    def exitId(self, ctx: asdParser.IdContext):
        ID = str(ctx.ID())

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            raise Exception(ctx.start.line, "undeclared variable: ", ID)
        else:
            type = self.getTypeStr(temp[0][1])
            self.generator.load("%" + str(ctx.ID()), type)
            self.stack.append(Value("%" + str(self.generator.reg - 1), temp[0][1]))

        pass


del asdParser