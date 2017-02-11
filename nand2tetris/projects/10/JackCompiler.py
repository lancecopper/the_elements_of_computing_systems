'''
PROGRAM_STRUCTURE = {"class", "class_var_dec", "type", "subroutine_dec", 
    "parameter_list", "subroutine_body", "var_dec"}
EXPRESSIONS = {"expression", "term", "subroutine_call", "expression_list"}
NON_TERMINALS = {"class", "class_var_dec", "subroutine_dec", "parameterlist",
    "subroutine_body", "var_dec", "statements", "while_statement", "if_statement",
    "return_statement", "let_statement", "do_statement", "expression", "term",
    "expression_list"}
is_class_name = is_identifier
is_subroutine_name = is_identifier
is_var_name = is_identifier
def is_type(token):
    return token in TYPE or is_identifier(token)
def is_integer_constant(token):
    return token.isdigit() and 0 <= int(token) <= 32767
def is_string_constant(token):
    midtoken = token[1:-1]
    return token.startswith("\"") and token.endswith("\"") and \
        "\"" not in midtoken and "\n" not in midtoken
def is_terminal(token):
    return is_keyword(token) or is_symbol(token) or is_integer_constant(token) \
        or is_string_constant(token) or is_identifier(token)
'''
import sys, os, collections, re, io
from functools import wraps
import getopt
KEYWORD = {"class", "constructor", "function", "method", "field",
    "static", "var", "int", "char", "boolean", "void", "true", "false",
    "null", "this", "let", "do", "if", "else", "while", "return"}
SYMBOL = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-",
    "*", "/", "&", "|", "<", ">", "=", "~"}
DIGIT = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
IDENTIFIER = re.compile(r"^[a-zA-z_][a-zA-z0-9_]*$")
OP = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OP = {"-", "~"}
KEYWORD_CONSTANT = {"true", "false", "null", "this"}
TYPE = {"int", "char", "boolean"}
TYPE_DICT = {"KEYWORD": "keyword",
             "SYMBOL": "symbol",
             "IDENTIFIER": "identifier",
             "INT_CONST": "integerConstant",
             "STRING_CONST": "stringConstant"}
def is_keyword(token):
    return token in KEYWORD
def is_symbol(token):
    return token in SYMBOL
def is_identifier(token):
    return re.match(IDENTIFIER, token) is not None
def strip_spacing_and_annot(cmd):
    annotation = cmd.find("//")
    if annotation != -1:
        cmd = cmd[:annotation]
    cmd = cmd.strip("\n").strip(" ")
    return cmd
def strip_spacing(cmd):
    cmd = cmd.strip("\n").strip(" ")
    return cmd
def dec_compile_prog(tag):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._output_script.write(" " * self._indent + "<{}>\n".format(tag))
            self._indent += 2
            #print("calling {}".format(func.__name__), self._indent)
            func(self, *args, *kwargs)
            self._indent -= 2
            #print("finish {}".format(func.__name__), self._indent)
            self._output_script.write(" " * self._indent + "</{}>\n".format(tag))
        return wrapper
    return decorator
class JackAnalyzer():
    def __init__(self, input_script_paths):
        assert(isinstance(input_script_paths, collections.deque))
        self._input_script_paths = input_script_paths
        self._scriptnum = len(input_script_paths)
        self._cur_script_path = None
    def has_more_script(self):
        return self._scriptnum > 0
    def advance(self):
        self._cur_script_path = self._input_script_paths.popleft()
        self._scriptnum -= 1
    def run(self):
        print("Analyzing {}".format(self._cur_script_path))
        with JackTokenizer(self._cur_script_path) as tokenizer:
            with CompilationEngine(tokenizer) as engine:
                engine.compile_class()
                if tokenizer.has_more_tokens():
                    raise SyntaxError("Redundant codes in script {} in line {}\
                        ".format(self._cur_script_path, tokenizer._line_num))
class JackTokenizer():
    def __init__(self, input_script_path):
        self._input_script_path = input_script_path
        self._cur_line = None
        self._next_line = None
        self._cur_token = None
        self._next_token = None
        self._cur_type = None
        self._next_type = None
        self._line_num = -1
        self._firstchar = None
    def __enter__(self):
        self._input_script = open(self._input_script_path, "rt")
        self._cur_line = io.StringIO(self._read_line(self._input_script))
        self._read_line(self._input_script)
        self.advance()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._input_script.close()
    def get_path(self):
        return self._input_script_path
    def get_token(self):
        return self._cur_token
    def get_next_token(self):
        return self._next_token
    def has_more_tokens(self):
        return self._next_token != ""
    def has_more_lines(self):
        return self._next_line != ""
    def read_token(self, io_text):
        # need to realise a finite-state machine
        self._next_type = None
        self._next_token = ""
        char = self._firstchar
        while char in {None, " ", "\n", "\r", "\t"}:
            char = io_text.read(1)
        if char.isalpha() or char == "_":
            while char.isalnum() or char == "_":
                self._next_token = self._next_token + char
                char = io_text.read(1)
            if is_keyword(self._next_token):
                self._next_type = "KEYWORD"
            elif is_identifier(self._next_token):
                self._next_type = "IDENTIFIER"
            else:
                raise ValueError("Unrecognizable token in line {}!".format(self._line_num))
        elif is_symbol(char):
            self._next_token = char
            char = " "
            self._next_type = "SYMBOL"
        elif char in DIGIT:
            while char in DIGIT:
                self._next_token = self._next_token + char
                char = io_text.read(1)
            self._next_token = int(self._next_token)
            self._next_type = "INT_CONST"
        elif char == "\"":
            char = io_text.read(1)
            while char not in {"\"", ""}:
                self._next_token = self._next_token + char
                char = io_text.read(1)
            if char == "\"":
                char = " "
                self._next_type = "STRING_CONST"
            else:
                raise ValueError("Encounter line feed while dealing with string !\
                    ".format(self._line_num))
        elif char == "":
            self._next_token = ""
            char = " "
            self._next_type = None
        else:
            raise ValueError("Unrecognizable token in line {}!".format(self._line_num))
        self._firstchar = char
    def _read_line(self, io_text):
        self._next_line = io_text.readline()
        self._line_num += 1
        if self._next_line != "":
            self._next_line = strip_spacing_and_annot(self._next_line)
            while self._next_line.startswith("/*") or \
                  self._next_line == "":
                if self._next_line.startswith("/*"):
                    while not self._next_line.endswith("*/"):
                        self._next_line = io_text.readline()
                        self._line_num += 1
                        if self._next_line == "":
                            raise ValueError("Incomplete annotation structure in line {}!\
                                ".format(self._line_num))
                        self._next_line = strip_spacing(self._next_line)
                    self._next_line = io_text.readline()
                    self._line_num += 1
                    if self._next_line == "":
                        break
                    else:
                        self._next_line = strip_spacing_and_annot(self._next_line)
                else:
                    self._next_line = io_text.readline()
                    self._line_num += 1
                    if self._next_line == "":
                        break
                    else:
                        self._next_line = strip_spacing_and_annot(self._next_line)
        return self._next_line
    def advance(self):
        #print(self._cur_token, self._next_token)
        assert(self.has_more_tokens())
        self._cur_token = self._next_token
        self._cur_type = self._next_type
        self.read_token(self._cur_line)
        if self._next_token == "" and self.has_more_lines():
            #print(self._next_line)
            self._cur_line = io.StringIO(self._next_line)
            self._read_line(self._input_script)
            self.read_token(self._cur_line)
    def token_type(self):
        return self._cur_type
    '''
    def next_token_type(self):
        return self._next_type
    '''
    def keyword(self):
        assert(self.token_type() == "KEYWORD")
        return self._cur_token
    def symbol(self):
        assert(self.token_type() == "SYMBOL")
        return self._cur_token
    def identifier(self):
        assert(self.token_type() == "IDENTIFIER")
        return self._cur_token
    def intval(self):
        assert(self.token_type() == "INT_CONST")
        return self._cur_token
    def stringval(self):
        assert(self.token_type() == "STRING_CONST")
        return self._cur_token
class CompilationEngine():
    def __init__(self, tokenizer):
        assert(isinstance(tokenizer, JackTokenizer))
        self._tokenizer = tokenizer
        self._output_script_path = self._tokenizer.get_path()[:-4] + "xml"
        self._indent = 0
    def __enter__(self):
        self._output_script = open(self._output_script_path, "wt")
        self._tokenizer.advance()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._output_script.close()
    def match(self, token_type, token = None):
        result = self._tokenizer.token_type() == token_type
        temp_token = self._tokenizer.get_token()
        if token:
            result = result and temp_token in token
        if result:
            if token_type == "INT_CONST":
                temp_token = str(temp_token)
            elif temp_token == "<":
                temp_token = "&lt;"
            elif temp_token == ">":
                temp_token = "&gt;"
            elif temp_token == "\"":
                temp_token == "&quote;"
            elif temp_token == "&":
                temp_token = "&amp;"
            token_type = TYPE_DICT[token_type]
            self._output_script.write(" " * self._indent + "<{}> ".format(token_type))
            self._output_script.write(temp_token)
            self._output_script.write(" </{}>\n".format(token_type))
            self._tokenizer.advance()
        else:
            if token:
                raise SyntaxError("Syntax Error in line {}: expected <{}> {}!\
                    ".format(self._tokenizer._line_num, token_type, token))
            else:
                raise SyntaxError("Syntax Error in line {}: expected <{}>!\
                    ".format(self._tokenizer._line_num, token_type))
        return result
    def match_type(self):
        if self._tokenizer.token_type() == "KEYWORD":
            self.match("KEYWORD", TYPE)
        elif self._tokenizer.token_type() == "IDENTIFIER":
            self.match("IDENTIFIER")
        else:
            SyntaxError("Syntax Error: expected <IDENTIFIER> or {} as [TYPE]!".format(TYPE))
    @dec_compile_prog("class")
    def compile_class(self):
        '''
        # class: 'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.match("KEYWORD", {"class"})
        self.match("IDENTIFIER")
        self.match("SYMBOL", {"{"})
        while self._tokenizer.get_token() in {"static", "field"}:
            self.compile_class_var_dec()
        while self._tokenizer.get_token() in {"constructor", "function", "method"}:
            self.compile_subroutine()
        try:
            self.match("SYMBOL", {"}"})
        except AssertionError as e:
            print("Match finished!  ~ (^_^)∠")
    @dec_compile_prog("classVarDec")
    def compile_class_var_dec(self):
        '''
        # classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        '''
        self.match("KEYWORD", {"static", "field"})
        self.match_type()
        self.match("IDENTIFIER")
        while self._tokenizer.get_token() == ",":
            self.match("SYMBOL", {","})
            self.match("IDENTIFIER")
        self.match("SYMBOL", {";"})
    @dec_compile_prog("subroutineDec")
    def compile_subroutine(self):
        '''
        # subroutineDec: ('constructor' | 'function' | 'method')
        #                ('void' | type) subroutineName '(' parameterList ')'
        #                subroutineBody
        '''
        self.match("KEYWORD", {"constructor", "function", "method"})
        if self._tokenizer.get_token() == "void":
            self.match("KEYWORD", {"void"})
        else:
            self.match_type()
        self.match("IDENTIFIER")
        self.match("SYMBOL", {"("})
        self.compile_parameter_list()
        self.match("SYMBOL", {")"})
        self.compile_subroutine_body()
    @dec_compile_prog("subroutineBody")
    def compile_subroutine_body(self):
        '''
        # subroutineBody: '{' varDec* statements '}'
        '''
        self.match("SYMBOL", {"{"})
        while self._tokenizer.get_token() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.match("SYMBOL", {"}"})
    @dec_compile_prog("parameterList")
    def compile_parameter_list(self):
        '''
        # parameterList: ((type varName) (',' type varName)*)?
        '''
        if self._tokenizer.get_token() != ")":
            self.match_type()
            self.match("IDENTIFIER")
        while self._tokenizer.get_token() == ",":
            self.match("SYMBOL", {","})
            self.match_type()
            self.match("IDENTIFIER")
    @dec_compile_prog("varDec")
    def compile_var_dec(self):
        '''
        # 'var' type varName (',' varName)* ';'
        '''
        self.match("KEYWORD", {"var"})
        self.match_type()
        self.match("IDENTIFIER")
        while self._tokenizer.get_token() == ",":
            self.match("SYMBOL", {","})
            self.match("IDENTIFIER")
        self.match("SYMBOL", {";"})
    @dec_compile_prog("statements")
    def compile_statements(self):
        '''
        # statements: statement*
        #  statement: letStatement | ifStatement | whileStatement |
        #             doStatement | returnStatement
        '''
        while True:
            temp_token = self._tokenizer.get_token()
            if temp_token == "let":
                self.compile_let()
            elif temp_token == "if":
                self.compile_if()
            elif temp_token == "while":
                self.compile_while()
            elif temp_token == "do":
                self.compile_do()
            elif temp_token == "return":
                self.compile_return()
            else:
                break
    @dec_compile_prog("letStatement")
    def compile_let(self):
        '''
        # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        '''
        self.match("KEYWORD", {"let"})
        self.match("IDENTIFIER")
        if self._tokenizer.get_token() == "[":
            self.match("SYMBOL", {"["})
            self.compile_expression()
            self.match("SYMBOL", {"]"})
        self.match("SYMBOL", {"="})
        self.compile_expression()
        self.match("SYMBOL", {";"})
    @dec_compile_prog("ifStatement")
    def compile_if(self):
        '''
        # ifStatement: 'if' '(' expression ')' '{' statements '}'
        '''
        self.match("KEYWORD", "if")
        self.match("SYMBOL", {"("})
        self.compile_expression()
        self.match("SYMBOL", {")"})
        self.match("SYMBOL", {"{"})
        self.compile_statements()
        self.match("SYMBOL", {"}"})
        if self._tokenizer.get_token() == "else":
            self.match("KEYWORD", "else")
            self.match("SYMBOL", {"{"})
            self.compile_statements()
            self.match("SYMBOL", {"}"})
    @dec_compile_prog("whileStatement")
    def compile_while(self):
        '''
        # whileStatement: 'while' '(' expression ')' '{' statements '}'
        '''
        self.match("KEYWORD", "while")
        self.match("SYMBOL", {"("})
        self.compile_expression()
        self.match("SYMBOL", {")"})
        self.match("SYMBOL", {"{"})
        self.compile_statements()
        self.match("SYMBOL", {"}"})
    @dec_compile_prog("doStatement")
    def compile_do(self):
        '''
        # doStatement: 'do' subroutineCall ';'
        '''
        self.match("KEYWORD", {"do"})
        self.match("IDENTIFIER")
        if self._tokenizer.get_token() == ".":
            self.match("SYMBOL", {"."})
            self.match("IDENTIFIER")
        self.match("SYMBOL", {"("})
        self.compile_expression_list()
        self.match("SYMBOL", {")"})
        self.match("SYMBOL", {";"})
    @dec_compile_prog("returnStatement")
    def compile_return(self):
        '''
        # ReturnStatement:  'return' expression? ';'
        '''
        self.match("KEYWORD", {"return"})
        if self._tokenizer.get_token() != ";":
            self.compile_expression()
        self.match("SYMBOL", {";"})
    @dec_compile_prog("expression")
    def compile_expression(self):
        '''
        # expression: term (op term)*
        '''
        self.compile_term()
        while self._tokenizer.get_token() in OP:
            self.match("SYMBOL", OP)
            self.compile_term()
    @dec_compile_prog("term")
    def compile_term(self):
        '''
        # term: integerConstant | stringConstant | keywordConstant |
        #       varName | varName '[' expression ']' | subroutineCall |
        #       '(' expression ')' | unaryOp term
        '''
        temp_token = self._tokenizer.get_token()
        temp_type = self._tokenizer.token_type()
        if temp_type == "INT_CONST":
            self.match("INT_CONST")
        elif temp_type == "STRING_CONST":
            self.match("STRING_CONST")
        elif temp_token in KEYWORD_CONSTANT:
            self.match("KEYWORD", KEYWORD_CONSTANT)
        elif temp_type == "IDENTIFIER":
            self.match("IDENTIFIER")
            temp_token = self._tokenizer.get_token()
            if temp_token == "[":
                self.match("SYMBOL", {"["})
                self.compile_expression()
                self.match("SYMBOL", {"]"})
            elif temp_token in {".", "("}:
                if temp_token == ".":
                    self.match("SYMBOL", {"."})
                    self.match("IDENTIFIER")
                self.match("SYMBOL", {"("})
                self.compile_expression_list()
                self.match("SYMBOL", {")"})
        elif temp_token == "(":
            self.match("SYMBOL", {"("})
            self.compile_expression()
            self.match("SYMBOL", {")"})
        elif temp_token in UNARY_OP:
            self.match("SYMBOL", UNARY_OP)
            self.compile_term()
    @dec_compile_prog("expressionList")
    def compile_expression_list(self):
        '''
        # expressionList: (expression (',' expression)* )?
        '''
        if self._tokenizer.get_token() != ")":
            self.compile_expression()
            while self._tokenizer.get_token() == ",":
                self.match("SYMBOL", {","})
                self.compile_expression()
def usage():
    print("{:<10}: help".format("-h"))
    print("{:<10}: test tokenizer".format("-t"))
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[2:], "ht")
    test_tokenizer = False
    for op, value in opts:
        if op == "-t":
            test_tokenizer = True
        if op == "-h":
            usage()
            sys.exit()    
    cur_path = sys.path[0]
    input_script_path = cur_path + '/' + sys.argv[1]
    if os.path.isdir(input_script_path):
        input_script_paths = collections.deque() 
        for root, dirs, files in os.walk(input_script_path):
            if root == input_script_path:
                for file in files:
                    if file.endswith('.jack'):
                        input_script_paths.append(input_script_path + '/' + file)
    elif os.path.isfile(input_script_path):
        if input_script_path.endswith('.vm'):
            input_script_paths = [input_script_path]
        else:
            raise ValueError("input file should be named '*.vm'")
    else:
        raise ValueError("input source is neither dir nor file")
    analyzer =  JackAnalyzer(input_script_paths)
    if not test_tokenizer:
        while analyzer.has_more_script():
            analyzer.advance()
            analyzer.run()
    else:
        for input_script_path in input_script_paths:
            with JackTokenizer(input_script_path) as parser:
                print("\n", input_script_path, "is parsing...")
                output_script_path = input_script_path[:-5] + "T.xml"
                with open(output_script_path, "wt") as output_script:
                    print("<tokens>", file = output_script)
                    while parser.has_more_tokens():
                        parser.advance()
                        temp_token = parser.get_token()
                        if temp_token == "<":
                            temp_token = "&lt;"
                        elif temp_token == ">":
                            temp_token = "&gt;"
                        elif temp_token == "\"":
                            temp_token == "&quote;"
                        elif temp_token == "&":
                            temp_token = "&amp;"
                        temp_type = TYPE_DICT[parser.token_type()]
                        print("<{0}> {1} </{0}>".format(temp_type, temp_token), file = output_script)
                    print("</tokens>", file = output_script)

            
