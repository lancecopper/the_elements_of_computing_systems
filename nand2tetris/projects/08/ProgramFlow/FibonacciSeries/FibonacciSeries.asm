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
@1
D=A
@R3
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@THAT
A=M
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@THAT
A=M
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
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
@2
D=A
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
@0
D=A
@ARG
A=M
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
(main.MAIN_LOOP_START)
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
@main.COMPUTE_ELEMENT
D;JNE
@main.END_PROGRAM
0;JMP
(main.COMPUTE_ELEMENT)
@THAT
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
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
@2
D=A
@THAT
A=M
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
@R3
D=A
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
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
@1
D=A
@R3
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
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
@1
D=A
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
@0
D=A
@ARG
A=M
D=A+D
@R5
M=D
@SP
AM=M-1
D=M
@R5
A=M
M=D
@main.MAIN_LOOP_START
0;JMP
(main.END_PROGRAM)
