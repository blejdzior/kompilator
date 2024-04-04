class LLVMgenerator:
    header_text = ""
    main_text = ""
    reg = 1

    def printf(self, id):
        reg = str(self.reg)
        id = str(id)
        self.main_text += "%" + reg +" = load i32, i32* %" + id + "\n"
        self.reg += 1
        reg = str(self.reg)
        self.main_text += "%" + reg + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strp, i32 0, i32 0), i32 %" \
                          + str(int(reg) - 1) + ")\n"
        self.reg += 1
        return self.main_text


    def scanf(self, id):
        reg = str(self.reg)
        self.main_text += "%" + reg + " = call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @strs, i32 0, i32 0), i32* %" + id + ")\n"
        self.reg += 1

    def declare(self, id):
        self.main_text += "%" + str(id) + " = alloca i32\n"

    def assign(self, id, value):
        self.main_text += "store i32 " + str(value) + ", i32* %" + str(id) + "\n"
    def generate(self):
        text = ""
        text += "declare i32 @printf(i8*, ...)\n"
        text += "declare i32 @__isoc99_scanf(i8*, ...)\n"
        text += "@strp = constant [4 x i8] c\"%d\\0A\\00\"\n"
        text += "@strs = constant [3 x i8] c\"%d\\00\"\n"
        text += self.header_text
        text += "define i32 @main() nounwind{\n"
        text += self.main_text
        text += "ret i32 0 }\n"
        return text

