class LLVMgenerator:
    header_text = ""
    main_text = ""
    reg = 1

    def printf_i32(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load i32, i32* %" + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpi, i32 0, i32 0), i32 %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1

    def printf_double(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) +" = load double, double* %" + id + "\n"
        self.reg += 1
        self.main_text += "%" + str(self.reg) + " = call double (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strpd, i32 0, i32 0), double %" \
                          + str(self.reg - 1) + ")\n"
        self.reg += 1

    def scanf(self, id):
        id = str(id)
        self.main_text += "%" + str(self.reg) + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @strs, i32 0, i32 0), i32* %" + id + ")\n"
        self.reg += 1

    # declare i32 variable
    def declare_i32(self, id):
        self.main_text += "%" + str(id) + " = alloca i32\n"

    # assign i32 value
    def assign_i32(self, id, value):
        self.main_text += "store i32 " + str(value) + ", i32* %" + str(id) + "\n"

    # declare double variable
    def declare_double(self, id):
        self.main_text += "%" + str(id) + " = alloca double\n"

    # assign double value
    def assign_double(self, id, value):
        self.main_text += "store double " + str(value) + ", double* %" + str(id) + "\n"
    def generate(self):
        text = ""
        text += "declare i32 @printf(i8*, ...)\n"
        text += "declare i32 @__isoc99_scanf(i8*, ...)\n"
        text += "@strpi = constant [4 x i8] c\"%d\\0A\\00\"\n";
        text += "@strpd = constant [4 x i8] c\"%f\\0A\\00\"\n";
        text += "@strs = constant [3 x i8] c\"%d\\00\"\n";
        text += self.header_text
        text += "define i32 @main() nounwind{\n"
        text += self.main_text
        text += "ret i32 0 }\n"
        return text

