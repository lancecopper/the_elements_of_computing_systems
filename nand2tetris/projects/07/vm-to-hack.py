import sys, os
ARITH_TO_ASM = {
    "add": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D+M\n",
    "sub": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=M-D\n",
    "neg": "@SP\nA=M-1\nM=-M\n",
    "eq": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JEQ\nD=0\n@{1}\n0;JMP\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "gt": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JGT\nD=0\n@{1}\n0;JMP\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "lt": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JLT\nD=0\n@{1}\n0;JEQ\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "and": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D&M\n",
    "or": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D|M\n",
    "not": "@SP\nA=M-1\nM=!M\n"
}
MEM_ACCESS_CMDS = {"push", "pop"}
PROG_FLOW_CMDS = {"label", "goto", "if-goto"}
FUNC_CALL_CMDS = {"function", "call", "return"}
CMD_TYPE_DICT = dict()
for cmd in ARITH_TO_ASM.keys():
    CMD_TYPE_DICT[cmd] = "C_ARITHMETIC"
for cmd in MEM_ACCESS_CMDS.union(PROG_FLOW_CMDS).union(FUNC_CALL_CMDS):
    if cmd == "if-goto":
        CMD_TYPE_DICT[cmd] = "C_IF"
    else:
        CMD_TYPE_DICT[cmd] = "C_" + cmd.upper()
MEM_AC_TO_ASM = {
    "push_constant": "@{}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_local": "@LCL\nD=M\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_argument": "@ARG\nD=M\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_this": "@THIS\nD=M\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_that": "@THAT\nD=M\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_temp": "@R5\nD=A\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_pointer": "@R3\nD=A\n@{}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "push_static": "@{}.{}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "pop_local": "@{}\nD=A\n@LCL\nA=M\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_argument": "@{}\nD=A\n@ARG\nA=M\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_this": "@{}\nD=A\n@THIS\nA=M\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_that": "@{}\nD=A\n@THAT\nA=M\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_temp": "@{}\nD=A\n@R5\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_pointer": "@{}\nD=A\n@R3\nD=A+D\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n",
    "pop_static": "@SP\nAM=M-1\nD=M\n@{}.{}\nM=D\n"
}
PROG_FLOW_TO_ASM = {
    "label": None,
    "goto": None,
    "if-goto": None
}
FUNC_CALL_TO_ASM ={
    "function": None,
    "call": None,
    "return": None,
}
def strip_spacing_and_annot(cmd):
    annotation = cmd.find("//")
    if annotation != -1:
        cmd = cmd[:annotation]
    cmd = cmd.strip("\n").strip(" ")
    return cmd
class Parser():
    def __init__(self, input_script_path):
        self._input_script_path = input_script_path
        self._input_script = None
        self._cur_command = None
        self._next_command = None
        self._cur_type = None
    def __enter__(self):
        self._input_script = open(self._input_script_path, "rt")
        self.advance()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._input_script.close()
    def has_more_commands(self):
        return self._next_command != ''
    def advance(self):
        self._cur_command = self._next_command
        self._next_command = self._input_script.readline()
        if self._next_command != "":
            self._next_command = strip_spacing_and_annot(self._next_command)
            while self._next_command == "":
                self._next_command = self._input_script.readline()
                if self._next_command == "":
                    break
                self._next_command = strip_spacing_and_annot(self._next_command)
        self._cur_type = None
        self._arg1 = None
        self._arg2 = None
        self._cur_tokens = None
    def command_type(self):
        if self._cur_type is None:
            if self._cur_command in ARITH_TO_ASM:
                self._cur_type = "C_ARITHMETIC"
                self._arg1 = self._cur_command
            else:
                self._cur_tokens = self._cur_command.split(' ')
                while '' in self._cur_tokens:
                    self._cur_tokens.remove('')
                self._cur_type = CMD_TYPE_DICT[self._cur_tokens[0]]
        return self._cur_type
    def arg1(self):
        assert(self.command_type() != "C_RETURN")
        if self._arg1 is None:
            self._arg1 = self._cur_tokens[1]
        return self._arg1
    def arg2(self):
        assert(self.command_type() in ("C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"))
        if self._arg2 is None:
            self._arg2 = self._cur_tokens[2]
        return self._arg2
class CodeWriter():
    def __init__(self, output_script_path):
        self._output_script_path = output_script_path
        self._output_script = None
        self._cur_file = None
        self._label_num = 0
    def __enter__(self):
        self._output_script = open(self._output_script_path, "wt")
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._output_script.close()
    def set_file_name(self, filename):
        self._cur_file = filename
    def write_arithmetic(self, command):
        if command in set(ARITH_TO_ASM.keys()) - {"eq", "gt", "lt"}:
            self._output_script.write(ARITH_TO_ASM[command])
        elif command in {"eq", "gt", "lt"}:
            tmplab0 = "label" + str(self._label_num)
            tmplab1 = "label" + str(self._label_num + 1)
            self._output_script.write(ARITH_TO_ASM[command].format(tmplab0, tmplab1))
            self._label_num += 2
        else:
            raise ValueError("unrecognizable C_ARITHMETIC arg1----{}".format(command))
    def write_push_pop(self, command, segment, index):
        assert(command in ("C_PUSH", "C_POP"))
        index = int(index)
        if command == "C_PUSH" and segment in \
            ("constant", "local", "argument", "this", "that", "temp", "pointer"):
            self._output_script.write(MEM_AC_TO_ASM["push_" + segment].format(index))
        elif command == "C_PUSH" and segment == "static":
            self._output_script.write(MEM_AC_TO_ASM["push_static"].format(self._cur_file, index))
        elif command == "C_POP" and segment in \
            ("local", "argument", "this", "that", "temp", "pointer"):
            self._output_script.write(MEM_AC_TO_ASM["pop_" + segment].format(index))
        elif command == "C_POP" and segment == "static":
            self._output_script.write(MEM_AC_TO_ASM["pop_static"].format(self._cur_file, index))
        else:
            raise SyntaxError("Illegal usage with seg {} and cmd {}".format(segment, command))
    def close(self):
        print("Do not use this method! Use python context manager!")
        pass
if __name__ == "__main__":
    cur_path = sys.path[0]
    input_script_path = cur_path + '/' + sys.argv[1]
    if os.path.isdir(input_script_path):
        input_script_paths = [] 
        output_script_path = input_script_path + '.asm'
        for root, dirs, files in os.walk(input_script_path):
            if root == input_script_path:
                for file in files:
                    if file.endswith('.vm'):
                        input_script_paths.append(input_script_path + '/' + file)
    elif os.path.isfile(input_script_path):
        if input_script_path.endswith('.vm'):
            output_script_path = input_script_path[:-2] + 'asm'
            input_script_paths = [input_script_path]
        else:
            raise ValueError("input file should be named '*.vm'")
    else:
        raise ValueError("input source is neither dir nor file")
    with CodeWriter(output_script_path) as codewriter:
        for input_script_path in input_script_paths:
            filename = input_script_path[input_script_path.rfind('/') + 1:-3]
            codewriter.set_file_name(filename)
            print("\n", input_script_path, "is parsing...")
            with Parser(input_script_path) as parser:
                while parser.has_more_commands():
                    parser.advance()
                    command_type = parser.command_type()
                    if command_type != "C_RETURN":
                        arg1 = parser.arg1()
                    if command_type in ("C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"):
                        arg2 = parser.arg2()
                    #print(command_type, arg1, arg2)
                    if command_type == "C_ARITHMETIC":
                        codewriter.write_arithmetic(arg1)
                    elif command_type in {"C_PUSH", "C_POP"}:
                        codewriter.write_push_pop(command_type, arg1, arg2)
                    else:
                        raise ValueError("unrecognizable command type")
