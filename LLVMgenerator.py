from value import Value

class LLVMgenerator:
    def __init__(self):
        self.header_text = ""
        self.main_text = ""
        self.reg = 1
        self.label_count = 0
        self.str = 1
        self.brstack = []
        self.br = 0
        self.result_text = ""
        self.main_reg = 1
        self.isFirstGenCall = True
        self.genPrintNr = 0


    

############ printf ###############
    def printf_array_element(self, id, type):
        self.main_text += f"%{self.reg} = alloca {type}\n"
        self.main_text += f"store {type} %{id}, {type}* %{self.reg}\n"
        self.reg += 1

    def printf_string(self, id):
        id = str(id)
        self.main_text += "%"+ str(self.reg) +" = load i8*, i8** "+id+"\n"
        self.reg += 1      
        self.main_text += "%"+ str(self.reg) +" = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strps, i32 0, i32 0), i8* %"+str(self.reg-1)+")\n"
        self.reg += 1

    # prints 'true' for value==1 and 'false' for value==0
    def printf_bool(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = load i1, i1* " + id + "\n"
        self.reg += 1
        # Select the appropriate string based on the boolean value
        self.main_text += "%" + str(self.reg) + " = select i1 %" + str(self.reg - 1) + ", i8* getelementptr inbounds ([5 x i8], [5 x i8]* @trueStr, i32 0, i32 0), i8* getelementptr inbounds ([6 x i8], [6 x i8]* @falseStr, i32 0, i32 0)\n"
        self.reg += 1
        # Call printf with the selected string
        self.main_text += "call i32 (i8*, ...) @printf(i8* %" + str(self.reg - 1) + ")\n"
        self.reg += 1
            
    def printf_i8(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i8, i8* " + id + "\n"
        self.reg += 1
        # promoting i8 to i32
        self.main_text += "%" + str(self.reg) + " = sext i8 %" + str(self.reg - 1) + " to i32\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    

    def printf_i16(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i16, i16* " + id + "\n"
        self.reg += 1
        # promoting i16 to i32
        self.main_text += "%" + str(self.reg) + " = sext i16 %" + str(self.reg - 1) + " to i32\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1

    def printf_i32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i32, i32* " + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
    def printf_i64(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i64, i64* " + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpl, i32 0, i32 0), i64 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1


    def printf_double(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load double, double* " + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpd, i32 0, i32 0), double %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
    def printf_float32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load float, float* " + id + "\n"
        self.reg += 1
        # Convert float to double
        self.main_text += "%" + str(self.reg) + " = fpext float %" + str(self.reg - 1) + " to double\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpd, i32 0, i32 0), double %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
######### scanf ###########

    def scanf_string(self, id, l=16):
        self.allocate_string("str"+str(self.str), l)
        id = str(id)
        # self.main_text += "%"+ id +" = alloca i8*\n"
        self.main_text += "%"+str(self.reg)+" = getelementptr inbounds ["+str(l+1)+" x i8], ["+str(l+1)+" x i8]* %str"+str(self.str)+", i64 0, i64 0\n"
        self.reg += 1
        self.main_text += "store i8* %"+str(self.reg-1)+", i8** "+id+"\n"
        self.str += 1
        self.main_text += "%"+str(self.reg)+" = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @strss, i32 0, i32 0), i8* %"+str(self.reg-1)+")\n"
        self.reg += 1



    # takes integer input, if input == 0 then false else true
    def scanf_bool(self, boolVar):
        # Assuming boolVar is the name of the variable where the boolean value will be stored.
        # First, declare a temporary integer variable to hold the scanf input.
        tempIntVar = "tempInt" + str(self.reg)
        self.main_text += "%" + tempIntVar + " = alloca i32\n"
        self.reg += 1

        # Use scanf to read an integer.
        self.main_text += "call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @strs, i32 0, i32 0), i32* %" + tempIntVar + ")\n"
        self.reg += 1

        # Load the read integer value.
        self.main_text += "%" + str(self.reg) + " = load i32, i32* %" + tempIntVar + "\n"
        loadedIntVar = self.reg
        self.reg += 1
        # Convert the integer to a boolean (i1) by comparing it to 0.
        # First, compute the comparison and store the result in a new temporary register
        self.main_text += "%" + str(self.reg) + " = icmp ne i32 %" + str(loadedIntVar) + ", 0\n"
        # Then, store the result of the comparison into the memory location pointed to by boolVar
        self.main_text += "store i1 %" + str(self.reg) + ", i1* %" + boolVar + "\n"
        # Increment the register counter
        self.reg += 1
    

    def scanf_float32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @strf, i32 0, i32 0), float* %" + id + ")\n"
        self.reg += 1
    
    def scanf_double(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strlf, i32 0, i32 0), double* %" + id + ")\n"
        self.reg += 1

    def scanf_int64(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpl, i32 0, i32 0), i64* %" + id + ")\n"
        self.reg += 1
    
    def scanf_int32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32* %" + id + ")\n"
        self.reg += 1
    
    def scanf_int16(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strhd, i32 0, i32 0), i16* %" + id + ")\n"
        self.reg += 1
    
    def scanf_int8(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strhhd, i32 0, i32 0), i8* %" + id + ")\n"
        self.reg += 1

########## LOAD ################

    def load(self, id, type):
        self.main_text += "%" + str(self.reg) + " = load " + str(type) + ", ptr " + str(id) + "\n"
        self.reg += 1

########## CHANGE_TYPE ################

    def increase_type(self, id, cur_type, target_type):
        self.main_text += "%" + str(self.reg) + " = sext " + str(cur_type) + " " + str(id) + " to " + str(target_type) + "\n"
        self.reg += 1

    def decrease_type(self, id, cur_type, target_type):
        self.main_text += "%" + str(self.reg) + " = trunc " + str(cur_type) + " " + str(id) + " to " + str(target_type) + "\n"
        self.reg += 1

    def double_to_float(self, id):
        self.main_text += "%" + str(self.reg) + " = fptrunc double " + str(id) + " to float\n"
        self.reg += 1

    def real_to_int(self, id, cur_type, target_type):
        self.main_text += "%" + str(self.reg) + " = fptosi " + str(cur_type) + " " + str(id) + " to " + str(target_type) + "\n"
        self.reg += 1

    def int_to_real(self, id, cur_type, target_type):
        self.main_text += "%" + str(self.reg) + " = uitofp " + str(cur_type) + " " + str(id) + " to " + str(target_type) + "\n"
        self.reg += 1

########## DECLARE ################


    def declare_struct(self, id, variables):
        self.header_text += f"%{id} = type " + '{'
        for index, v in enumerate(variables):
            if index == len(variables) - 1:
                self.header_text += f"{v.type}"
            else:
                self.header_text += f"{v.type}, "
        self.header_text += "}\n"

    def declare_array(self, id, type, size, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + f" = global [{size} x {type}] zeroinitializer\n"
        else:
            self.main_text += f"%{id} = alloca [{size} x {type}]\n"

    def declare_matrix(self, id, type, rows, cols, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + f" = global [{rows} x <{cols} x {type}>] zeroinitializer\n"
        else:
            self.main_text += f"%{id} = alloca [{rows} x <{cols} x {type}>]\n"

    def declare_string(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global [1 x i8] c\"\\00\"\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i8*\n"

    def allocate_string(self, id, l):
        self.main_text += "%"+str(id)+" = alloca ["+str(l+1)+" x i8]\n"
    
    def constant_string(self, content):
        l = len(content)+1
        l = str(l)
        self.header_text += "@str"+str(self.str)+" = constant ["+l+" x i8] c\""+content+"\\00\"\n"
        n = "str"+str(self.str)
        self.allocate_string(n, int(l)-1)
        self.main_text += "%"+str(self.reg)+" = bitcast ["+l+" x i8]* %"+n+" to i8*\n"
        self.main_text += "call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 1 %"+str(self.reg)+", i8* align 1 getelementptr inbounds (["+l+" x i8], ["+l+" x i8]* @"+n+", i32 0, i32 0), i64 "+l+", i1 false)\n"
        self.reg += 1
        self.main_text += "%ptr"+n+" = alloca i8*\n"
        self.main_text += "%"+str(self.reg)+" = getelementptr inbounds ["+l+" x i8], ["+l+" x i8]* %"+n+", i64 0, i64 0\n"
        self.reg += 1
        self.main_text += "store i8* %"+str(self.reg-1)+", i8** %ptr"+n+"\n"
        self.str += 1
   
    # declare boolean
    def declare_bool(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global i1 0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i1\n"

    # declare i8 variable
    def declare_i8(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global i8 0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i8\n"

    # declare i16 variable
    def declare_i16(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global i16 0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i16\n"
    
    # declare i32 variable
    def declare_i32(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global i32 0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i32\n"

    # declare i64 variable
    def declare_i64(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global i64 0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca i64\n"

    # declare f32 variable
    def declare_float32(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global float 0.0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca float\n"

    # declare double variable
    def declare_double(self, id, is_global):
        if is_global:
            self.header_text += "@"+ str(id) + " = global double 0.0\n"
        else:
            self.main_text += "%" + str(id) + " = alloca double\n"
    
########## ASSIGN ############
    def assign_struct(self, id, structID, is_global):
        if is_global:
            self.header_text += f"{id} = global %{structID} zeroinitializer\n"
        else:
            self.main_text += f"{id} = alloca %{structID}\n"

    def assign_struct_member(self, id, name, index, value, type):
        self.main_text += f"%{self.reg} = getelementptr %{name}, %{name}* {id}, i32 0, i32 {index}\n"
        self.main_text += f"store {type} {value}, {type}* %{self.reg}\n"
        self.reg += 1

    def struct_access(self, id, name, index, type):
        self.main_text += f"%{self.reg} = getelementptr %{name}, %{name}* {id}, i32 0, i32 {index}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = load {type}, {type}* %{self.reg - 1}\n"
        self.reg += 1

    def assign_matrix(self, id, type, rows, cols, lines):
        for i in range(rows):
            self.main_text += f"%{self.reg} = getelementptr inbounds [ {rows} x <{cols} x {type}>], ptr {id}, i64 0, i64 {i}\n"
            temp = self.reg
            self.reg += 1
            self.main_text += f"%{self.reg} = load <{cols} x {type}>, ptr %{self.reg - 1}\n"
            self.reg += 1
            for j in range(cols):
                self.main_text += f"%{self.reg} = insertelement <{cols} x {type}> %{self.reg - 1}, {type} {lines[i][j]}, i32 {j}\n"
                self.reg += 1
            self.main_text += f"store <{cols} x {type} > %{self.reg - 1}, ptr %{temp}\n"

    def matrix_access(self, id, indexes, type, rows, cols):
        row_index = indexes[0]
        col_index = indexes[1]
        self.main_text += f"%{self.reg} = getelementptr inbounds [{rows} x <{cols} x {type} >], ptr {id}, i64 0, i64 {row_index}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = load <{cols} x {type}>, ptr %{self.reg - 1}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = extractelement <{cols} x {type}> %{self.reg-1}, i64 {col_index}\n"
        self.reg += 1

    def matrix_element_assign(self, id, indexes, value, type, rows, cols):
        row_index = indexes[0]
        col_index = indexes[1]
        self.main_text += f"%{self.reg} = getelementptr inbounds [{rows} x <{cols} x {type} >], ptr {id}, i64 0, i64 {row_index}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = getelementptr inbounds[{cols} x {type}], ptr %{self.reg-1}, i64 0, i64 {col_index}\n"
        self.main_text += f"store {type} {value}, ptr %{self.reg}\n"
        self.reg += 1


    def array_access(self, id, index, type, size):
        self.main_text += f"%{self.reg} = getelementptr inbounds[{size} x {type}], ptr {id}, i64 0, i64 {index}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = load {type}, {type}* %{self.reg - 1}\n"
        self.reg += 1

    def element_assign(self, id, index, value, type, size):
        self.main_text += f"%{self.reg} = getelementptr inbounds[{size} x {type}], ptr {id}, i64 0, i64 {index}\n"
        self.main_text += f"store {type} {value}, ptr %{self.reg}\n"
        self.reg += 1


    def assign_array(self, id, type, size, values):
        for i in range(len(values)):
            self.element_assign(id, i, values[i], type, size)



    def assign_string(self, id, value):
        self.main_text += "store i8* %"+str(self.reg-1)+", i8** "+str(id)+"\n"
   

    # assign boolean value
    def assign_bool(self, id, value):
        # if isinstance(value, int):
            self.main_text += "store i1 " + str(value) + ", i1* " + str(id) + "\n"
        # else:
        #     self.reg += 1
        #     self.main_text += "%" + id + " = load i1, i1* " + value + '\n'

    
    # assign i8 value
    def assign_i8(self, id, value):
        self.main_text += "store i8 " + str(value) + ", i8* " + str(id) + "\n"
    
    # assign i16 value
    def assign_i16(self, id, value):
        self.main_text += "store i16 " + str(value) + ", i16* " + str(id) + "\n"

    # assign i32 value
    def assign_i32(self, id, value):
        self.main_text += "store i32 " + str(value) + ", i32* " + str(id) + "\n"
    
    # assign i64 value
    def assign_i64(self, id, value):
        self.main_text += "store i64 " + str(value) + ", i64* " + str(id) + "\n"
    
    # assign float32 value
    def assign_float32(self, id, value):
        self.main_text += "store float " + str(value) + ", float* " + str(id) + "\n"

    # assign double value
    def assign_double(self, id, value):
        self.main_text += "store double " + str(value) + ", double* " + str(id) + "\n"

######## BOOLEAN OPERATIONS #############
    def NegOp(self, value):
        self.XorOp(value, Value('true', 3))
    
    def XorOp(self, value1, value2):
        # check for value1 content
        try:
            if value1.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
                
            elif value1.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
            elif value1.name is not None:
                value1 = value1.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value1 + ", i1* %" + str(self.reg) + '\n'
                value1 = str(self.reg)
                self.reg += 1
                
        except AttributeError:
            print("value is a variable name")
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value1 + "\n"
        value1 = str(self.reg)
        self.reg += 1
        # check for value2 content
        try:
            if value2.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)

                self.reg += 1
            elif value2.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)
                self.reg += 1
            elif value2.name is not None:
                value2 = value2.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value2 + ", i1* %" + str(self.reg) + '\n'
                value2 = str(self.reg)
                self.reg += 1
        
                
        except AttributeError:
            print("value is a variable name")
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value2 + "\n"
        value2 = str(self.reg)
        self.reg += 1

        self.main_text += "%" + str(self.reg) + " = xor i1 %" + value1 + ", %" + value2 + "\n"
        self.reg += 1

    def orOp(self, value1, value2):
         # Generate labels for branching
        evalSecondLabel = f"evalSecond{self.label_count}"
        endLabel = f"endLogicalOr{self.label_count}"
        finalFalse = f"finalFalse{self.label_count}"
        finalTrue = f"finalTrue{self.label_count}"
        self.label_count += 1

        # perform check for value1 content
        try:
            if value1.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
                
            elif value1.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
            elif value1.name is not None:
                value1 = value1.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value1 + ", i1* %" + str(self.reg) + '\n'
                value1 = str(self.reg)
                self.reg += 1
                
        except AttributeError:
            print("value is a variable name")
        
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value1 + "\n"
        self.reg += 1
    
        # Evaluate the first operand (assuming it's already a boolean expression)
        # and branch based on its value
        self.main_text += f"br i1 %{str(self.reg - 1)}, label %{finalTrue}, label %{evalSecondLabel}\n"

        # Label for evaluating the second operand
        self.main_text += f"{evalSecondLabel}:\n"
        try:
            if value2.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)

                self.reg += 1
            elif value2.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)
                self.reg += 1
            elif value2.name is not None:
                value2 = value2.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value2 + ", i1* %" + str(self.reg) + '\n'
                value2 = str(self.reg)
                self.reg += 1
                
        except AttributeError:
            print("value is a variable name")
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value2 + "\n"
        self.reg += 1
        
        self.main_text += f'br i1 %{str(self.reg - 1)}, label %{finalTrue}, label %{finalFalse}\n'
        # Direct branch to end after evaluation
        self.main_text += f"{finalTrue}:\n"
        self.main_text += f"br label %{endLabel}\n"
        self.main_text += f"{finalFalse}:\n"
        self.main_text += f"br label %{endLabel}\n"

        # End label where result is determined
        self.main_text += f"{endLabel}:\n"
        # Use phi to select the result based on the branch taken
        resultReg = self.reg
        self.reg += 1
        self.main_text += f"%{resultReg} = phi i1 [1, %{finalTrue}], [0, %{finalFalse}]\n"


    def andOp(self, value1, value2):
        # Generate labels for branching
        evalSecondLabel = f"evalSecond{self.label_count}"
        endLabel = f"endLogicalAnd{self.label_count}"
        finalFalse = f"finalFalse{self.label_count}"
        finalTrue = f"finalTrue{self.label_count}"
        self.label_count += 1

        # perform check for value1 content
        try:
            if value1.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
                
            elif value1.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value1 = str(self.reg)
                self.reg += 1
            elif value1.name is not None:
                value1 = value1.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value1 + ", i1* %" + str(self.reg) + '\n'
                value1 = str(self.reg)
                self.reg += 1
                
        except AttributeError:
            print("value is a variable name")
        
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value1 + "\n"
        self.reg += 1
    
        # Evaluate the first operand (assuming it's already a boolean expression)
        # and branch based on its value
        self.main_text += f"br i1 %{str(self.reg - 1)}, label %{evalSecondLabel}, label %{finalFalse}\n"

        # Label for evaluating the second operand
        self.main_text += f"{evalSecondLabel}:\n"
        try:
            if value2.name == 'false':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 0, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)

                self.reg += 1
            elif value2.name == 'true':
                self.main_text += '%' + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 1, i1* %" + str(self.reg) + "\n"
                value2 = str(self.reg)
                self.reg += 1
            elif value2.name is not None:
                value2 = value2.name
                self.main_text += "%" + str(self.reg) + ' = alloca i1\n'
                self.main_text += "store i1 " + value2 + ", i1* %" + str(self.reg) + '\n'
                value2 = str(self.reg)
                self.reg += 1
                
        except AttributeError:
            print("value is a variable name")
        self.main_text += "%" + str(self.reg) + " = load i1, i1* %" + value2 + "\n"
        self.reg += 1
        
        self.main_text += f'br i1 %{str(self.reg - 1)}, label %{finalTrue}, label %{finalFalse}\n'
        # Direct branch to end after evaluation
        self.main_text += f"{finalTrue}:\n"
        self.main_text += f"br label %{endLabel}\n"
        self.main_text += f"{finalFalse}:\n"
        self.main_text += f"br label %{endLabel}\n"

        # End label where result is determined
        self.main_text += f"{endLabel}:\n"
        # Use phi to select the result based on the branch taken
        resultReg = self.reg
        self.reg += 1
        self.main_text += f"%{resultReg} = phi i1 [1, %{finalTrue}], [0, %{finalFalse}]\n"



######## ARITHMETIC OPERATIONS ###########
    
    def add_i64(self, value1, value2):
        self.main_text += "%" + str(self.reg) + " = add i64 " + str(value1) + ", " + str(value2) + "\n"
        self.reg += 1

    def add_i32(self, value1, value2):
        self.main_text += "%" + str(self.reg) + " = add i32 " + str(value1) + ", " + str(value2) + "\n"
        self.reg += 1

    def add_double(self, value1, value2):
        self.main_text += "%" + str(self.reg) + " = fadd double " + str(value1) + ", " + str(value2) + "\n"
        self.reg += 1

    def sub_i64(self, value1, value2):
        self.main_text += "%" + str(self.reg) + " = sub i64 " + str(value1) + ", " + str(value2) + "\n"
        self.reg += 1

    def sub_double(self, value1, value2):
        self.main_text += "%" + str(self.reg) + " = fsub double " + str(value1) + ", " + str(value2) + "\n"
        self.reg += 1

    def mult_i64(self, val1, val2):
        self.main_text += "%" + str(self.reg) + " = mul i64 " + str(val1) + ", " + str(val2) + "\n"
        self.reg += 1

    def mult_double(self, val1, val2):
        self.main_text += "%" + str(self.reg) + " = fmul double " + str(val1) + ", " + str(val2) + "\n"
        self.reg += 1


    def div_i64(self, val1, val2):
        self.main_text += "%" + str(self.reg) + " = sdiv i64 " + str(val1) + ", " + str(val2) + "\n"
        self.reg += 1


    def div_double(self, val1, val2):
        self.main_text += "%" + str(self.reg) + " = fdiv double " + str(val1) + ", " + str(val2) + "\n"
        self.reg += 1


#############  IF  ##################

    def icmp(self, id, value):
        self.main_text += "%"+ str(self.reg) +" = load i32, i32* "+id+"\n"
        self.reg += 1
        self.main_text += "%"+ str(self.reg) + " = icmp eq i32 %" + str(self.reg-1) + ", " + str(value) + "\n"
        self.reg += 1


    def ifstart(self):
        self.br += 1
        self.main_text += "br i1 %"+str(self.reg-1)+", label %true"+ str(self.br) +", label %false"+ str(self.br) +"\n"
        self.main_text += "true"+ str(self.br) +":\n"
        self.brstack.append(self.br)


    def ifend(self):
        b = self.brstack.pop()
        self.main_text += "br label %false"+ str(b) +"\n"
        self.main_text += "false" + str(b) + ":\n"

##################  REPEAT  ###############

    def repeatstart(self, repetitions):
        self.declare_i32(str(self.reg), False)
        counter = self.reg
        self.reg += 1
        self.assign_i32('%'+str(counter), 0)
        self.br += 1
        self.main_text += "br label %cond"+ str(self.br) +"\n"
        self.main_text += "cond"+ str(self.br) +":\n"

        self.load("%"+str(counter), 'i32')
        self.add_i32("%"+str(self.reg-1), 1)
        self.assign_i32('%'+str(counter), "%"+str(self.reg-1))

        self.main_text += "%"+ str(self.reg) +" = icmp slt i32 %"+ str(self.reg-2) +", "+ str(repetitions) + "\n"
        self.reg += 1

        self.main_text += "br i1 %"+ str(self.reg-1)+", label %true"+ str(self.br) +", label %false"+ str(self.br) +"\n"
        self.main_text += "true"+ str(self.br)+":\n"
        self.brstack.append(self.br)


    def repeatend(self):
        b = self.brstack.pop()
        self.main_text += "br label %cond"+ str(b) +"\n"
        self.main_text += "false"+ str(b) +":\n"


###########  FUNCTION  #############
    def methodStart(self, id, type, classID):
        self.result_text += self.main_text
        self.main_reg = self.reg
        self.main_text = "define " + str(type) + " @"+str(id)+f"(%{classID}* %this) " + "nounwind {\n"
        self.reg = 1


    def functionstart(self, id, type):
        self.result_text += self.main_text
        self.main_reg = self.reg
        self.main_text = "define " + str(type) + " @"+str(id)+"() nounwind {\n"
        self.reg = 1


    def functionend(self, type):
        self.main_text += "ret " + str(type) + " %" + str(self.reg-1) + "\n"
        self.main_text += "}\n"
        self.header_text += self.main_text
        self.main_text = ""
        self.reg = self.main_reg

    def close_main(self):
        self.result_text += self.main_text

    def call(self, id, type):
        self.main_text += "%" + str(self.reg) + " = call " + str(type) + " @" + str(id) + "()\n"
        self.reg += 1

    def callMethod(self, classID, funID, ID, type, is_global):

        self.main_text += f"%{self.reg} = getelementptr %{classID}, %{classID}* {ID}\n"
        self.reg += 1
        self.main_text += f"%{self.reg} = call {type} @{funID} (ptr %{self.reg - 1})\n"
        self.reg += 1


        # if not is_global:
        #     if classID == 'ptr':
        #         self.main_text += f"%{self.reg} = call {type} @{funID} ({classID} {ID})\n"
        #     else:
        #         self.main_text += f"%{self.reg} = call {type} @{funID} (%{classID} {ID})\n"

        #     self.reg += 1
        # else:

################    GENERATORY  ####################
    def gen_context(self, id, type):
        text = "%" + str(id) + "_context = type {\n"
        text += "i8*,\n"
        text += str(type) + '\n}\n'

        return text

    def gen_setup(self, id, type):
        text = f"define void @{str(id)}_setup(%{str(id)}_context* %context) nounwind " + "{\n"
        text += f"%1 = getelementptr %{str(id)}_context, %{str(id)}_context* %context, i32 0, i32 0\n"
        text += f"store i8* blockaddress(@{str(id)}_yield, %.yield1), i8** %1\n"
        text += "ret void\n}\n"

        return text

    def gen_start(self, id, type):
        self.result_text += self.main_text
        self.main_text = ""
        self.main_reg = self.reg
        self.header_text += self.gen_context(id, type)
        self.header_text += self.gen_setup(id, type)
        self.header_text += f"define i1 @{id}_yield(%{id}_context* %context) nounwind " + "{\n"
        self.header_text += f"%1 = getelementptr %{id}_context, %{id}_context* %context, i32 0, i32 0\n"
        self.header_text += f"%2 = load i8**, ptr %1\n"
        self.reg = 3

    def gen_end(self, _id, _type, nr_of_yields):
        self.main_text += "ret i1 0\n"
        self.main_text += "}\n"
        table_content = "".join([f", label %.yield{str(i)}" for i in range(2, nr_of_yields + 1)])
        self.header_text += f"indirectbr i8* %2, [ label %.yield1" + table_content + ']\n'
        self.header_text += f".yield1:\n"
        self.header_text += self.main_text
        self.main_text = ""
        self.reg = self.main_reg

    def _yield(self, gen_id, value, type, yield_nr):
        self.main_text += f"%{str(self.reg)} = getelementptr %{str(gen_id)}_context, %{str(gen_id)}_context* %context, i32 0, i32 1\n"
        self.main_text += f"store {type} {value}, ptr %{str(self.reg)}\n"
        self.reg += 1
        self.main_text += f"%{str(self.reg)} = getelementptr %{str(gen_id)}_context, %{str(gen_id)}_context* %context, i32 0, i32 0\n"
        self.main_text += f"store i8* blockaddress(@{str(gen_id)}_yield, %.yield{str(yield_nr+1)}), i8** %{str(self.reg)}\n"
        self.reg += 1
        self.main_text += f"ret i1 1\n"
        self.main_text += f".yield{str(yield_nr+1)}:\n"

    def call_gen(self, _id, _type):
        if self.isFirstGenCall:
            self.main_text += f"%context = alloca %{str(_id)}_context\n"
            self.main_text += f"call void @{str(_id)}_setup(%{str(_id)}_context* %context)\n"

        self.isFirstGenCall = False
        self.main_text += "%" + str(self.reg) + " = call i1 @" + str(_id) + f"_yield(%{str(_id)}_context* %context)\n"
        self.reg += 1
        self.main_text += f"%{str(self.reg)} = getelementptr %{str(_id)}_context, %{str(_id)}_context* %context, i32 0, i32 1\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + f" = load {_type}, ptr %" + str(self.reg-1) + "\n"
        self.reg += 1

    def print_gen(self, _id, _type):
        if self.isFirstGenCall:
            self.main_text += f"%context = alloca %{str(_id)}_context\n"
            self.isFirstGenCall = False

        self.main_text += f"call void @{str(_id)}_setup(%{str(_id)}_context* %context)\n"
        self.main_text += f"br label %.head{str(self.genPrintNr)}\n"

        self.main_text += f".head{str(self.genPrintNr)}:\n"

        self.main_text += f"%{self.reg} = call i1 @{str(_id)}_yield(%{str(_id)}_context* %context)\n"
        self.reg += 1
        self.main_text += f"br i1 %{self.reg-1}, label %.body{str(self.genPrintNr)}, label %.tail{str(self.genPrintNr)}\n"

        self.main_text += f".body{str(self.genPrintNr)}:\n"

        self.main_text += f"%{str(self.reg)} = getelementptr %{str(_id)}_context, %{str(_id)}_context* %context, i32 0, i32 1\n"
        self.reg += 1

        self.main_text += "%" + str(self.reg) + f" = load {_type}, ptr %" + str(self.reg - 1) + "\n"
        self.reg += 1
        type_first_letter = 'd' if (_type == 'double' or _type == 'float') else 'i'
        self.main_text += "%" + str(self.reg) + f" = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strp{type_first_letter}, i32 0, i32 0), {_type} %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
        self.main_text += f"br label %.head{str(self.genPrintNr)}\n"

        self.main_text += f".tail{str(self.genPrintNr)}:\n"

        self.genPrintNr += 1

    def generate(self):
        text = "\n\n\n"
        text += "declare i32 @printf(ptr, ...)\n"
        text += "declare i32 @__isoc99_scanf(i8*, ...)\n"
        text += "declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg)\n"
        text += "@strpi = constant [4 x i8] c\"%d\\0A\\00\"\n"
        text += "@strpd = constant [4 x i8] c\"%f\\0A\\00\"\n"
        text += "@strs = constant [3 x i8] c\"%d\\00\"\n"
        text += "@strss = constant [5 x i8] c\"%10s\\00\"\n"
        text += "@strf = constant [3 x i8] c\"%f\\00\"\n"
        text += "@strpl = constant [5 x i8] c\"%lld\\00\"\n"
        text += "@strlf = constant [4 x i8] c\"%lf\\00\"\n"
        text += "@strhhd = constant [5 x i8] c\"%hhd\\00\"\n"
        text += "@strhd = constant [4 x i8] c\"%hd\\00\"\n"
        text += "@trueStr = constant [5 x i8] c\"true\\00\"\n"
        text += "@falseStr = constant [6 x i8] c\"false\\00\"\n"
        text += "@strps = constant [4 x i8] c\"%s\\0A\\00\"\n"
        text += self.header_text
        text += "define i32 @main() nounwind{\n"
        text += self.result_text
        text += "ret i32 0 }\n"
        return text

