//'func SimpleFunction.test 2' start...
(SimpleFunction.test)
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
//'func SimpleFunction.test 2' end!
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
A=M-1
M=D+M
@SP
A=M-1
M=!M
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
A=M-1
M=D+M
@ARG
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
@SP
A=M-1
M=M-D
//'return' start...
@LCL
D=M
@R5
M=D
@5
A=D-A
D=M
@R6
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R5
A=M-1
D=M
@THAT
M=D
@2
D=A
@R5
A=M-D
D=M
@THIS
M=D
@3
D=A
@R5
A=M-D
D=M
@ARG
M=D
@4
D=A
@R5
A=M-D
D=M
@LCL
M=D
@R6
A=M
0;JMP
//'return' end!
