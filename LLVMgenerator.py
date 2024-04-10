class LLVMgenerator:
    header_text = ""
    main_text = ""
    reg = 1

############ printf ###############
    def printf_i8(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i8, i8* %" + id + "\n"
        self.reg += 1
        # promoting i8 to i32
        self.main_text += "%" + str(self.reg) + " = sext i8 %" + str(self.reg - 1) + " to i32\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
    def printf_i16(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i16, i16* %" + id + "\n"
        self.reg += 1
        # promoting i16 to i32
        self.main_text += "%" + str(self.reg) + " = sext i16 %" + str(self.reg - 1) + " to i32\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1

    def printf_i32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i32, i32* %" + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
    def printf_i64(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i64, i64* %" + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpl, i32 0, i32 0), i64 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1


    def printf_double(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load double, double* %" + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpd, i32 0, i32 0), double %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
    def printf_float32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load float, float* %" + id + "\n"
        self.reg += 1
        # Convert float to double
        self.main_text += "%" + str(self.reg) + " = fpext float %" + str(self.reg - 1) + " to double\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpd, i32 0, i32 0), double %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1
    
######### scanf ###########
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


    

########## DECLARE ################

    # declare i8 variable
    def declare_i8(self, id):
        self.main_text += "%" + str(id) + " = alloca i8\n"

    # declare i16 variable
    def declare_i16(self, id):
        self.main_text += "%" + str(id) + " = alloca i16\n"
    
    # declare i32 variable
    def declare_i32(self, id):
        self.main_text += "%" + str(id) + " = alloca i32\n"

    # declare i64 variable
    def declare_i64(self, id):
        self.main_text += "%" + str(id) + " = alloca i64\n"

    # declare f32 variable
    def declare_float32(self, id):
        self.main_text += "%" + str(id) + " = alloca float\n"

    # declare double variable
    def declare_double(self, id):
        self.main_text += "%" + str(id) + " = alloca double\n"
    
########## ASSIGN ############
    # assign i8 value
    def assign_i8(self, id, value):
        self.main_text += "store i8 " + str(value) + ", i8* %" + str(id) + "\n"
    
    # assign i16 value
    def assign_i16(self, id, value):
        self.main_text += "store i16 " + str(value) + ", i16* %" + str(id) + "\n"

    # assign i32 value
    def assign_i32(self, id, value):
        self.main_text += "store i32 " + str(value) + ", i32* %" + str(id) + "\n"
    
    # assign i64 value
    def assign_i64(self, id, value):
        self.main_text += "store i64 " + str(value) + ", i64* %" + str(id) + "\n"
    
    # assign float32 value
    def assign_float32(self, id, value):
        self.main_text += "store float " + str(value) + ", float* %" + str(id) + "\n"

    # assign double value
    def assign_double(self, id, value):
        self.main_text += "store double " + str(value) + ", double* %" + str(id) + "\n"





    def generate(self):
        text = "\n\n\n"
        text += "declare i32 @printf(ptr, ...)\n"
        text += "declare i32 @__isoc99_scanf(i8*, ...)\n"
        text += "@strpi = constant [4 x i8] c\"%d\\0A\\00\"\n"
        text += "@strpd = constant [4 x i8] c\"%f\\0A\\00\"\n"
        text += "@strs = constant [3 x i8] c\"%d\\00\"\n"
        text += "@strf = constant [3 x i8] c\"%f\\00\"\n"
        text += "@strpl = constant [5 x i8] c\"%lld\\00\"\n"
        text += "@strlf = constant [4 x i8] c\"%lf\\00\"\n"
        text += "@strhhd = constant [5 x i8] c\"%hhd\\00\"\n"
        text += "@strhd = constant [4 x i8] c\"%hd\\00\"\n"

        text += self.header_text
        text += "define i32 @main() nounwind{\n"
        text += self.main_text
        text += "ret i32 0 }\n"
        return text

