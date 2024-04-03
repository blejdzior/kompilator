class LLVMgenerator:
    header_text = ""
    main_text = ""
    reg = 1

    def printf(self, value):
        reg = str(self.reg)
        value = str(value)
        self.main_text += "%"+reg+" = load i32, i32* %"+value+"\n"
        self.reg += 1
        reg = str(self.reg)
        self.main_text += "%" + reg + " = call i32 (ptr, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @strp, i32 0, i32 0), i32 %" \
                          + str(int(reg) - 1) + ")\n"
        self.reg += 1
        return self.main_text



    def generate(self):

