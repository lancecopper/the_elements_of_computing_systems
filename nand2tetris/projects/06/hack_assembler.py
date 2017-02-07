import sys
import re
re_symbol = re.compile(r'^[a-zA-z_.$:][a-zA-z0-9_.$:]*$')
DEST_DICT = {'nil': '000', 'M': '001', 'D': '010', 'MD': '011',
             'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP_DICT = {'nil': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
             'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}
COMP_DICT = {'0': '0101010', '1': '0111111', '-1': '0111010',
             'D': '0001100', 'A': '0110000', '!D': '0001101',
             '!A': '0110001', '-D': '0001111', '-A': '0110011',
             'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
             'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
             'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
             'M': '1110000', '!M': '1110001', '-M': '1110011',
             'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
             'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000',
             'D|M': '1010101'}
symbol_table = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3,
                'THAT': 4, 'SCREEN': 16384, 'KBD': '24576'}
for i in range(16):
    symbol_table['R' + str(i)] = i
free_mem_ptr = 16
inst_addr = 0
def issymbol(token):
    result = re.match(re_symbol, token)
    return result is not None
def isdecimal(token):
    return token.isnumeric()
class Parser():
    def __init__(self, input_script_path):
        self._input_script_path = input_script_path
        self._input_script = None
        self._cur_command = None
        self._next_command = None
        self._cur_type = None
        self._cur_symbol = None
        self._cur_dest = None
        self._cur_comp = None
        self._cur_jump = None
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
        if self._next_command == "":
            pass
        else:
            annotation = self._next_command.find("//")
            if annotation != -1:
                self._next_command = self._next_command[:annotation]
            self._next_command = self._next_command.strip("\n").strip(" ")
            while self._next_command.startswith('//') or self._next_command == "":
                self._next_command = self._input_script.readline()
                if self._next_command == "":
                    break
                annotation = self._next_command.find("//")
                if annotation != -1:
                    self._next_command = self._next_command[:annotation]
                self._next_command = self._next_command.strip("\n").strip(" ")
        self._cur_type = None
        self._cur_symbol = None
        self._cur_dest = None
        self._cur_comp = None
        self._cur_jump = None
    def command_type(self):
        if self._cur_type:
            return self._cur_type
        if self._cur_command[0] == "@" and \
        (issymbol(self._cur_command[1:]) or isdecimal(self._cur_command[1:])):
            self._cur_symbol = self._cur_command[1:]
            self._cur_type = "A_COMMAND"
            return "A_COMMAND"
        elif self._cur_command[0] == "(" and self._cur_command[-1] == ")":
            if issymbol(self._cur_command[1:-1]):
                self._cur_symbol = self._cur_command[1:-1]
                self._cur_type = "L_COMMAND"
                return "L_COMMAND"
            else:
                raise ValueError("illegal symbal name, {}".format(self._cur_command[1:-1]))
        else:
            find_eqsign = self._cur_command.find("=")
            find_semicolon = self._cur_command.find(";")
            if find_eqsign == -1:
                self._cur_dest = "nil"
                comp_start = 0
            else:
                self._cur_dest = self._cur_command[:find_eqsign]
                comp_start = find_eqsign + 1
            if find_semicolon == -1:
                self._cur_jump = "nil"
                comp_end = len(self._cur_command)
            else:
                self._cur_jump = self._cur_command[find_semicolon + 1:]
                comp_end = find_semicolon
            if comp_start >= comp_end:
                raise ValueError("command cannot be parsed!")
            self._cur_comp = self._cur_command[comp_start:comp_end]
            self._cur_type = "C_COMMAND"
            return "C_COMMAND"
    def symbol(self):
        assert(self.command_type() in ["A_COMMAND", "L_COMMAND"])
        return self._cur_symbol
    def dest(self):
        assert(self.command_type() == "C_COMMAND")
        return self._cur_dest
    def comp(self):
        assert(self.command_type() == "C_COMMAND")
        return self._cur_comp
    def jump(self):
        assert(self.command_type() == "C_COMMAND")
        return self._cur_jump
class Code():
    def __init__(self, token):
        self.token = token
    def dest(self):
        return DEST_DICT[self.token]
    def comp(self):
        return COMP_DICT[self.token]
    def jump(self):
        return JUMP_DICT[self.token]

if __name__ == "__main__":
    cur_path = sys.path[0]
    input_script_path = cur_path + '/' + sys.argv[1]
    output_script_name = sys.argv[1][:sys.argv[1].find('.asm')]
    output_script_path = cur_path + '/' + output_script_name + '.hack'
    with Parser(input_script_path) as parser:
        result = []
        while parser.has_more_commands():
            parser.advance()
            command_type = parser.command_type()
            if command_type in ("A_COMMAND", "C_COMMAND"):
                inst_addr += 1
            elif command_type == "L_COMMAND":
                symbol = parser.symbol()
                if symbol not in symbol_table:
                    symbol_table[symbol] = inst_addr
                else:
                    raise ValueError("duplicative label definition, {}".format(symbol))
            else:
                raise ValueError("unrecognizable command type, {}".format(command))
    with open(output_script_path, "wt") as output_script:
        with Parser(input_script_path) as parser:
            result = []
            while parser.has_more_commands():
                parser.advance()
                command_type = parser.command_type()
                if command_type == "A_COMMAND":
                    symbol = parser.symbol()
                    if issymbol(symbol):
                        if symbol not in symbol_table:
                            symbol_table[symbol] = free_mem_ptr
                            free_mem_ptr += 1
                        symbol = symbol_table[symbol]
                    avalue = int(symbol)
                    if avalue > 32767:
                        raise ValueError("avalue > 32767")
                    bina = bin(avalue)[2:]
                    output_script.write(bina.zfill(16) + '\n')
                elif command_type == "C_COMMAND":
                    dest = Code(parser.dest()).dest()
                    comp = Code(parser.comp()).comp()
                    jump = Code(parser.jump()).jump()
                    output_script.write('111' + comp + dest + jump + '\n')
                elif command_type == "L_COMMAND":
                    pass
                else:
                    raise ValueError("unrecognizable command type, {}".format(command))


                





