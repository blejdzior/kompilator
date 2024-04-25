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
    STRUCT = 11
    CLASS = 12


class Listener(asdListener):
    def __init__(self):
        self.generator = LLVMgenerator()
        self.variables = []
        self.stack = []
        self.int = ['i8', 'i16', 'i32', 'i64']
        self.float = ['f32', 'f64']
        self.ints = [VarType.INT8, VarType.INT16, VarType.INT32, VarType.INT64]
        self.floats = [VarType.REAL32, VarType.REAL64]
        self.isGlobal = True
        self.function = ""
        self.functions = []
        self.localvariables = []
        self.structs = []
        self.funType = 'i64'
        self.fun_gens = []
        self.yieldNr = 1
        self.classID = ''
        self.class_variables = []

    # Enter a parse tree produced by asdParser#prog.
    def enterProg(self, ctx: asdParser.ProgContext):
        pass

    # Exit a parse tree produced by asdParser#prog.
    def exitProg(self, ctx: asdParser.ProgContext):
        self.generator.close_main()
        result = self.generator.generate()
        print(result)
        f = open("result.ll", "w")
        f.write(result)
        f.close()


    # var inside struct
    def exitVarDeclaration(self, ctx: asdParser.VarDeclarationContext):
        ID = ctx.var().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
        except:
            print(f"Line: {ctx.start.line}, struct variable must have type declaration")
            return
        if type == 'string':
            print(f"Line: {ctx.start.line}, no strings in struct")
            return
        type = self.string_to_type(type)
        if self.classID == '':
            self.stack.append(Value(ID, type))

    # # array inside struct
    # def exitArrayDeclaration(self, ctx: asdParser.ArrayDeclarationContext):
    #     ID = ctx.var.ID().symbol.text
    #     try:
    #         type = ctx.var.type().symbol.text
    #     except:
    #         print(f"Line: {ctx.start.line}, struct variable must have type declaration")
    #         return
    #     type = self.string_to_type(type)
    #     size = ctx.INT().symbol.text
    #     self.stack.append(Value(ID, (VarType.ARRAY, type, size)))
    
    # # matrix inside struct
    # def exitMatrixDeclaration(self, ctx: asdParser.MatrixDeclarationContext):
    #     ID = ctx.var.ID().symbol.text
    #     try:
    #         type = ctx.var.type().symbol.text
    #     except:
    #         print(f"Line: {ctx.start.line}, struct variable must have type declaration")
    #         return
    #     type = self.string_to_type(type)
    #     rows = ctx.INT(0).symbol.text
    #     cols = ctx.INT(1).symbol.text
    #     self.stack.append(Value(ID, (VarType.MATRIX, type, rows, cols)))
    def exitBlockclass(self, ctx:asdParser.BlockclassContext):
        self.classID = ''
        i = 0
        for var in ctx.declaration():
            i += 1
        self.stack.append(Value(i, VarType.STRUCT))
    
    def exitClass(self, ctx:asdParser.ClassContext):
        pass
    
    def exitClassAssign(self, ctx:asdParser.ClassAssignContext):
        ID = ctx.var().ID().symbol.text
        classID = ctx.classId().ID().symbol.text

        try:
            type = ctx.var().type_().getText()
        except:
            type = None
        if type is not None:
            raise Exception(ctx.start.line, "class variable can't have type definition")

        temp = [(x, y, z) for x, y, z in self.structs if x == classID]
        if len(temp) == 0:
            print(f"Line: {ctx.start.line}, class not defined")
            return
        
        is_global = self.isGlobal
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            is_global = True
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
        

        if is_global:
            self.variables.append((ID, (VarType.STRUCT, classID)))
            ID = '@' + ID
        else:
            self.localvariables.append((ID, (VarType.STRUCT, classID)))
            ID = '%' + ID

        self.class_variables.append((ID, classID))

        self.generator.assign_struct(ID, classID, is_global)

        # calling constructor
        temp = [(x, y) for x, y in self.functions if x == classID + '_Create_Default']
        if len(temp) != 0:
            self.generator.callMethod(classID, classID + '_Create_Default', ID, temp[0][1], is_global)
        else:
            raise Exception(ctx.start.line, "constructor not defined")
        

    def exitBlockstruct(self, ctx: asdParser.BlockstructContext):
        i = 0
        for var in ctx.declaration():
            i += 1
        self.stack.append(Value(i, VarType.STRUCT))

    def exitStruct(self, ctx: asdParser.StructContext):
        ID = ctx.structId().ID().symbol.text
        try:
            type = ctx.var().type_().getText()
        except:
            type = None
        if type is not None:
            raise Exception(ctx.start.line, "struct can't have type definition")

        struct = self.stack.pop()
        if struct.type != VarType.STRUCT:
            print("Line: " + str(ctx.start.line) + "struct definition not of type struct")
            return
        
        if struct.name == 0:
            print("Line: " + str(ctx.start.line) + ", struct cannot be initialized without values")
            return

        variables = []
        for i in range(struct.name):
            v = self.stack.pop()
            variables.append(v)
        variables.reverse()
        self.structs.append((ID, struct.name, variables))
        for v in variables:
            v.type = self.type_to_string(v.type)

        self.generator.declare_struct(ID, variables)
        

    def exitStructAssign(self, ctx:asdParser.StructAssignContext):
        ID = ctx.var().ID().symbol.text
        structID = ctx.structId().ID().symbol.text

        try:
            type = ctx.var().type_().getText()
        except:
            type = None
        if type is not None:
            raise Exception(ctx.start.line, "struct variable can't have type definition")

        temp = [(x, y, z) for x, y, z in self.structs if x == structID]
        if len(temp) == 0:
            print(f"Line: {ctx.start.line}, struct not defined")
            return
        
        is_global = self.isGlobal
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            is_global = True
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
        

        if is_global:
            self.variables.append((ID, (VarType.STRUCT, structID)))
            ID = '@' + ID
        else:
            self.localvariables.append((ID, (VarType.STRUCT, structID)))
            ID = '%' + ID

        self.generator.assign_struct(ID, structID, is_global)
    
    def exitMemberAssign(self, ctx: asdParser.MemberAssignContext):
        structID = ctx.ID().symbol.text
        memberID = ctx.var().ID().symbol.text
        value = self.stack.pop()
        isSelf = False
        if structID == 'self':
            structName = self.classID
            isSelf = True       

        is_global = self.isGlobal
        if not isSelf:
            temp = [(x, y) for x, y in self.variables if x == structID]
            if len(temp) != 0:
                is_global = True
            else:
                temp = [(x, y) for x, y in self.localvariables if x == structID]
                if len(temp) != 0:
                    is_global = False
                else:
                    print(f"Line:{ctx.start.line}, undefined variable {structID}")
                    return
            struct = [(x, y, z) for x, y, z in self.structs if temp[0][1][1] == x]
        else:
            struct = [(x, y, z) for x, y, z in self.structs if structName == x]

        variables = struct[0][2]
        structName = struct[0][0]
        structVarCount = struct[0][1]
        type = None
        i = 0
        for i in range(structVarCount):
            if memberID == variables[i].name:
                type = variables[i].type
                break;
        if value.type != self.string_to_type(type):
            print(f"Line: {ctx.start.line} wrong type of value")
            return


        if is_global:
            structID = '@' + structID
        else:
            structID = '%' + structID

        if isSelf:
            structID = '%this'
        self.generator.assign_struct_member(structID, structName, i, value.name, type)
    
    def exitMemberAccess(self, ctx:asdParser.MemberAccessContext):
        structID = ctx.ID().symbol.text
        memberID = ctx.var().ID().symbol.text

        isSelf = False
        if structID == 'self':
            structName = self.classID
            isSelf = True       

        is_global = self.isGlobal

        if not isSelf:
            temp = [(x, y) for x, y in self.variables if x == structID]
            if len(temp) != 0:
                is_global = True
            else:
                temp = [(x, y) for x, y in self.localvariables if x == structID]
                if len(temp) != 0:
                    is_global = False
                else:
                    print(f"Line:{ctx.start.line}, undefined variable {structID}")
                    return
            struct = [(x, y, z) for x, y, z in self.structs if temp[0][1][1] == x]
        else:
            struct = [(x, y, z) for x, y, z in self.structs if structName == x]

        variables = struct[0][2]
        structName = struct[0][0]
        structVarCount = struct[0][1]
        type = None
        i = 0
        for i in range(structVarCount):
            if memberID == variables[i].name:
                type = variables[i].type
                break;

        if is_global:
            structID = '@' + structID
        else:
            structID = '%' + structID

        if isSelf:
            structID = '%this'
        self.generator.struct_access(structID, structName, i, type)

        self.stack.append(Value("%" + str(self.generator.reg - 1), self.string_to_type(type)))


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
        is_global = True
        if len(temp) != 0:
            matrix_type, type, rows, cols = temp[0][1]
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                matrix_type, type, rows, cols = temp[0][1]
            else:
                print(f"Line: {ctx.start.line}, variable {ID} not declared")
                return

        if int(indexes[0]) >= rows or int(indexes[1]) >= cols:
            print(f"Line: {ctx.start.line}, index out of range")
            return
        if len(temp) == 0 or matrix_type != VarType.MATRIX:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        self.generator.matrix_access(ID, indexes, type=self.type_to_string(type), rows=rows, cols=cols)

        # type = self.string_to_type(type)

        self.stack.append(Value("%" + str(self.generator.reg - 1), type))


    def exitArrayAccess(self, ctx: asdParser.ArrayAccessContext):
        ID = ctx.ID().symbol.text
        index = ctx.INT().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        is_global = True
        if len(temp) != 0:
            arr_type, type, size = temp[0][1]
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                arr_type, type, size = temp[0][1]
            else:
                print(f"Line: {ctx.start.line}, variable {ID} not declared")
                return

        if int(index) >= size:
            print(f"Line: {ctx.start.line}, index out of range")
            return

        if len(temp) == 0 or arr_type != VarType.ARRAY:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        self.generator.array_access(ID, index, type=self.type_to_string(type), size=size)

        # type = self.string_to_type(type)

        self.stack.append(Value("%" + str(self.generator.reg - 1), type))


    def exitMatrixElementAssign(self, ctx: asdParser.ElementAssignContext):
        ID = ctx.ID().symbol.text
        indexes = (ctx.INT(0).symbol.text, ctx.INT(1).symbol.text)

        temp = [(x, y) for x, y in self.variables if x == ID]
        is_global = True
        if len(temp) != 0:
            matrix_type, type, rows, cols = temp[0][1]
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                matrix_type, type, rows, cols = temp[0][1]
            else:
                print(f"Line: {ctx.start.line}, variable {ID} not declared")
                return

        if int(indexes[0]) >= rows or int(indexes[1]) >= cols:
            print(f"Line: {ctx.start.line}, index out of range")
            return
        if len(temp) == 0 or matrix_type != VarType.MATRIX:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        value = self.stack.pop()
        self.generator.matrix_element_assign(ID, indexes, value.name, type=self.type_to_string(type), rows=rows, cols=cols)

    def exitElementAssign(self, ctx: asdParser.ElementAssignContext):
        ID = ctx.ID().symbol.text
        index = ctx.INT().symbol.text


        temp = [(x, y) for x, y in self.variables if x == ID]
        is_global = True
        if len(temp) != 0:
            arr_type, type, size = temp[0][1]
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                arr_type, type, size = temp[0][1]
            else:
                print(f"Line: {ctx.start.line}, variable {ID} not declared")
                return

        if int(index) >= size:
            print(f"Line: {ctx.start.line}, index out of range")
            return
        if len(temp) == 0 or arr_type != VarType.ARRAY:
            print(f"Line: {ctx.start.line}, variable {ID} not declared")
            return

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        value = self.stack.pop()
        self.generator.element_assign(ID, index, value.name, type=self.type_to_string(type), size=size)

    def exitMatrixAssign(self, ctx: asdParser.MatrixAssignContext):
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None

        is_global = self.isGlobal
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            is_global = True
            if type != temp[0][1][1]:
                type = temp[0][1][1]
                type = self.string_to_type(type)
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                if type != temp[0][1][1]:
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
            self.generator.declare_matrix(ID, type = type, rows = rows, cols = cols, is_global=is_global)
            self.variables.append((ID, (matrix.type, self.string_to_type(type), rows, cols)))

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        self.generator.assign_matrix(ID, type = type, rows = rows, cols = cols, lines = lines)




    def exitArrayAssign(self, ctx: asdParser.ArrayAssignContext):
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None


        is_global = self.isGlobal
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            is_global = True
            if type != temp[0][1][1]:
                type = temp[0][1][1]
                type = self.string_to_type(type)
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                if type != temp[0][1][1]:
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
        print(arr.type, self.string_to_type(type), arr.name)

        if len(temp) == 0:
            self.generator.declare_array(ID, type = type, size = arr.name, is_global=is_global)
            self.variables.append((ID, (arr.type, self.string_to_type(type), arr.name)))

        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID

        self.generator.assign_array(ID, type = type, size = arr.name, values = values)


    # Exit a parse tree produced by asdParser#assign.
    def exitAssign(self, ctx: asdParser.AssignContext):
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
            elif type == 'bool':
                type = VarType.BOOL
            elif type == 'str':
                type = VarType.STRING
        except AttributeError:
            type = None

        # Can assign var to var if: try: value = self.stack.pop() except IndexError: value = ctx.value().ID().symbol.text
        value = self.stack.pop()

        is_global = self.isGlobal
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            type = temp[0][1]
            is_global = True
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                is_global = False
                type = temp[0][1]

        # if no declared type then get type of value
        if type == None:
            type = value.type


        # if ID is not in self.variables
        if len(temp) == 0 and value.name[0] != '%':
            # check if declared type matches value type
            if type in self.ints and value.type in self.ints:
                bitlen = int(value.name).bit_length()
                if type == VarType.INT8 and bitlen in range(8):  # i8
                    self.generator.declare_i8(ID, is_global)
                elif type == VarType.INT16 and bitlen in range(16):  # i16
                    self.generator.declare_i16(ID, is_global)
                elif type == VarType.INT32 and bitlen in range(32):  # i32
                    self.generator.declare_i32(ID, is_global)
                elif type == VarType.INT64 and bitlen in range(64):  # i64
                    self.generator.declare_i64(ID, is_global)
                else:
                    print("Line: " + str(ctx.start.line) + ", integer number is too large to write to " + str(type))
                    return
            elif type in self.floats and value.type in self.floats:
                if type == VarType.REAL32:  # f32
                    self.generator.declare_float32(ID, is_global)
                elif type == VarType.REAL64:  # f64
                    self.generator.declare_double(ID, is_global)
            elif type == 'bool' or type == VarType.BOOL or value.type == VarType.BOOL:
                self.generator.declare_bool(ID, is_global)
            elif type == VarType.STRING:
                self.generator.declare_string(ID, is_global)
            elif type == None:  # no declared type
                if value.type == VarType.INT32:
                    self.generator.declare_i32(ID, is_global)
                elif value.type == VarType.REAL64:
                    self.generator.declare_double(ID, is_global)
                elif value.type == VarType.STRING:
                    self.generator.declare_string(ID, is_global)

            else:
                print("Line: " + str(ctx.start.line) + ", VarType and ValueType mismatch", type, value.type)
                return

            if is_global:
                if type:
                    self.variables.append((ID, type))
                else:
                    self.variables.append((ID, value.type))
            else:
                if type:
                    self.localvariables.append((ID, type))
                else:
                    self.localvariables.append((ID, value.type))

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

        if is_global:
            ID = "@" + ID
        else:
            ID = "%" + ID

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
        elif string == 'str':
            return VarType.STRING
        elif string == 'f32':
            return VarType.REAL32
        elif string == 'f64':
            return VarType.REAL64
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
        else:
            return type




    # Exit a parse tree produced by asdParser#print.
    def exitPrint(self, ctx: asdParser.PrintContext):
        ID = ctx.value().ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            ID = '@' + ID
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                ID = '%' + ID
            else:
                print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))

        _type = temp[0][1]
        try:
            if _type[0] == VarType.ARRAY:
                v = self.stack.pop()
                ID = v.name[1:]
                _type = v.type[1]
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
                self.generator.printf_string(ID)
            else:
                print("Line: " + str(ctx.start.line) + ", unknown variable type")


    # Enter a parse tree produced by asdParser#read.
    def enterRead(self, ctx: asdParser.ReadContext):
        pass

    # Exit a parse tree produced by asdParser#read.
    def exitRead(self, ctx: asdParser.ReadContext):
        ID = ctx.ID().symbol.text
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            ID = '@' + ID
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                ID = '%' + ID
            else:
                print("Line " + str(ctx.start.line) + ", unknown variable: " + str(ID))
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


    # Enter a parse tree produced by asdParser#blockif.
    def enterBlockif(self, ctx: asdParser.BlockifContext):
        self.generator.ifstart()

    # Exit a parse tree produced by asdParser#blockif.
    def exitBlockif(self, ctx: asdParser.BlockifContext):
        self.generator.ifend()

    # Exit a parse tree produced by asdParser#equal.
    def exitEqual(self, ctx: asdParser.EqualContext):
        ID = ctx.ID().getText()
        INT = ctx.INT().getText()
        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) != 0:
            self.generator.icmp('@' + ID, INT)
        else:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) != 0:
                self.generator.icmp('%' + ID, INT)
            else:
                raise Exception("Line " + str(ctx.start.line) + ", unknown variable: "+ str(ID))


    # Exit a parse tree produced by asdParser#repsNr.
    def exitRepsNr(self, ctx:asdParser.RepsNrContext):
        if ctx.ID() is None:
            value = ctx.INT().getText()
        else:
            ID = '%' + ctx.ID().getText()
            self.generator.load(ID, 'i32')
            value = '%' + str(self.generator.reg - 1)

        self.generator.repeatstart(value)


    # Exit a parse tree produced by asdParser#blockwhile.
    def exitBlockwhile(self, ctx:asdParser.BlockwhileContext):
        self.generator.repeatend()

    def enterClass(self, ctx:asdParser.ClassContext):
        ID = ctx.classId().ID().symbol.text
        self.classID = ID
        try:
            type = ctx.var().type_().getText()
        except:
            type = None
        if type is not None:
            raise Exception(ctx.start.line, "class can't have type definition")

        i = 0
        variables = []
        for declaration in ctx.blockclass().declaration():
            _type = declaration.var().type_().getText()
            if _type == 'f64':
                _type = 'double'
            elif _type == 'f32':
                _type = 'float'
            elif _type == 'bool':
                _type = 'i1'
            elif _type == 'str':
                _type = 'i8*'
            variables.append(Value(declaration.var().ID().symbol.text, _type))
            i += 1

        self.generator.declare_struct(ID, variables)

        self.structs.append((self.classID, i, variables))
        


    def exitMethodType(self, ctx:asdParser.MethodTypeContext):
        _type = ctx.type_().getText()
        if _type == 'f64':
            _type = 'double'
        elif _type == 'f32':
            _type = 'float'
        elif _type == 'bool':
            _type = 'i1'
        elif _type == 'str':
            _type = 'i8*'
        else: 
            _type = 'i64'

        self.funType = _type
    




    def exitMethodId(self, ctx:asdParser.MethodIdContext):
        ID = str(ctx.ID())
        if ID == self.classID:
            ID = self.classID + '_Create_Default'
        else:
            ID = self.classID + '_' + str(ctx.ID())
        self.functions.append((ID, self.funType))
        self.function = ID
        self.generator.methodStart(ID, self.funType, self.classID)

    def enterBlockmethod(self, ctx:asdParser.BlockmethodContext):
        self.isGlobal = False

    def exitBlockmethod(self, ctx:asdParser.BlockmethodContext):
        temp = [(x, y) for x, y in self.localvariables if x == self.function]
        if len(temp) == 0:
            self.generator.declare_i32(self.function, False)
            self.generator.assign_i32("%"+str(self.function), 0)
        #   "%"+self.function

        self.generator.load("%"+str(self.function), self.funType)
        self.generator.functionend(self.funType)
        self.localvariables = []
        self.isGlobal = True

        # Exit a parse tree produced by asdParser#function.
    def exitFunction(self, ctx:asdParser.FunctionContext):
        self.funType = 'i64'

    # Exit a parse tree produced by asdParser#funType.
    def exitFunType(self, ctx:asdParser.FunTypeContext):
        _type = ctx.type_().getText()
        if _type == 'f64':
            _type = 'double'
        elif _type == 'f32':
            _type = 'float'
        elif _type == 'bool':
            _type = 'i1'
        elif _type == 'str':
            _type = 'i8*'

        self.funType = _type

    # Exit a parse tree produced by asdParser#funId.
    def exitFunId(self, ctx:asdParser.FunIdContext):
        ID = str(ctx.ID())
        self.functions.append((ID, self.funType))
        self.function = ID
        self.generator.functionstart(ID, self.funType)

    # Enter a parse tree produced by asdParser#blockfun.
    def enterBlockfun(self, ctx:asdParser.BlockfunContext):
        self.isGlobal = False

    # Exit a parse tree produced by asdParser#blockfun.
    def exitBlockfun(self, ctx:asdParser.BlockfunContext):
        temp = [(x, y) for x, y in self.localvariables if x == self.function]
        if len(temp) == 0:
            self.generator.declare_i32(self.function, False)
            self.generator.assign_i32("%"+str(self.function), 0)
        #   "%"+self.function

        self.generator.load("%"+str(self.function), self.funType)
        self.generator.functionend(self.funType)
        self.localvariables = []
        self.isGlobal = True

    # Exit a parse tree produced by asdParser#call.
    def exitCall(self, ctx:asdParser.CallContext):
        ID = str(ctx.ID())

        temp = [(x, y) for x, y in self.functions if x == ID]
        if len(temp) == 0:
            temp = [(x, y) for x, y in self.fun_gens if x == ID]
            if len(temp) == 0:
                raise Exception(ctx.start.line, "undeclared function: ", ID, self.functions)
            else:
                self.generator.call_gen(ID)
                self.stack.append(Value("%" + str(self.generator.reg - 1), self.getTypeVarType(temp[0][1])))
        else:
            self.generator.call(ID, temp[0][1])
            self.stack.append(Value("%" + str(self.generator.reg - 1), self.getTypeVarType(temp[0][1])))
    
    def exitMethodCall(self, ctx:asdParser.MethodCallContext):
        ID = str(ctx.ID())
        methodID = str(ctx.var().ID())
        is_global = self.isGlobal
        if is_global:
            ID = '@' + ID
        else:
            ID = '%' + ID
        temp = [(x, y) for x, y in self.class_variables if x == ID]
        classID = temp[0][1]
        temp = [(x, y) for x, y in self.functions if x == classID + '_' + methodID]
        if len(temp) != 0:
            self.generator.callMethod(classID, classID + '_' + methodID, ID, temp[0][1], is_global)
        else:
            raise Exception(ctx.start.line, "method not defined")
        self.stack.append(Value("%" + str(self.generator.reg - 1), self.getTypeVarType(temp[0][1])))

    # Exit a parse tree produced by asdParser#generator.
    def exitGenerator(self, ctx:asdParser.GeneratorContext):
        self.generator.gen_end(self.function, self.funType, self.yieldNr)
        self.funType = 'i64'
        self.isGlobal = True

    # Exit a parse tree produced by asdParser#genType.
    def exitGenType(self, ctx:asdParser.GenTypeContext):
        _type = ctx.type_().getText()
        if _type == 'f64':
            _type = 'double'
        elif _type == 'f32':
            _type = 'float'
        elif _type == 'bool':
            _type = 'i1'
        elif _type == 'str':
            _type = 'i8*'

        self.funType = _type

    # Exit a parse tree produced by asdParser#genId.
    def exitGenId(self, ctx:asdParser.GenIdContext):
        ID = str(ctx.ID())
        self.fun_gens.append((ID, self.funType))
        self.function = ID
        self.generator.gen_start(self.function, self.funType)

    # Enter a parse tree produced by asdParser#blockGen.
    def enterBlockGen(self, ctx:asdParser.BlockGenContext):
        self.isGlobal = False

    # Exit a parse tree produced by asdParser#blockGen.
    def exitBlockGen(self, ctx:asdParser.BlockGenContext):
        self.localvariables = []

    # Exit a parse tree produced by asdParser#yieldExpr.
    def exitYieldExpr(self, ctx:asdParser.YieldExprContext):
        try:
            value = ctx.value().INT().symbol.text
        except:
            try:
                value = '%' + ctx.value().ID().symbol.text
                self.generator.load(value, 'i32')
                value = '%' + str(self.generator.reg-1)
            except:
                raise Exception(ctx.start.line, "unallowed expression")

        self.generator._yield(self.function, value, self.funType, self.yieldNr)
        self.yieldNr += 1

    # Exit a parse tree produced by asdParser#printGen.
    def exitPrintGen(self, ctx:asdParser.PrintGenContext):
        ID = str(ctx.genPrintId().ID())
        self.generator.print_gen(ID)

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

    def getTypeVarType(self, _type):
        if _type == 'i8':
            _type = VarType.INT8
        elif _type == 'i16':
            _type = VarType.INT16
        elif _type == 'i32':
            _type = VarType.INT32
        elif _type == 'i64':
            _type = VarType.INT64
        elif _type == 'f32' or _type == 'float':
            _type = VarType.REAL32
        elif _type == 'f64' or _type == 'double':
            _type = VarType.REAL64
        elif _type == 'bool' or _type == 'i1':
            _type = VarType.BOOL
        elif _type == 'str' or _type == 'i8*':
            _type = VarType.STRING

        return _type

    # Exit a parse tree produced by asdParser#id.
    def exitId(self, ctx: asdParser.IdContext):
        ID = str(ctx.ID())

        temp = [(x, y) for x, y in self.variables if x == ID]
        if len(temp) == 0:
            temp = [(x, y) for x, y in self.localvariables if x == ID]
            if len(temp) == 0:
                raise Exception(ctx.start.line, "undeclared variable: ", ID)
            else:
                type = self.getTypeStr(temp[0][1])
                self.generator.load("%" + str(ctx.ID()), type)
                self.stack.append(Value("%" + str(self.generator.reg - 1), temp[0][1]))
        else:
            type = self.getTypeStr(temp[0][1])
            if type == None:
                type = self.getTypeStr(temp[0][1][1])

            self.generator.load("@" + str(ctx.ID()), type)
            self.stack.append(Value("%" + str(self.generator.reg - 1), temp[0][1]))

        pass


del asdParser