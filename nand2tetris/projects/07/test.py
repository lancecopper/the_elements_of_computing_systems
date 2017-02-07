ARITH_TO_ASM = {
    "add": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D+M\n",
    "sub": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=M-D\n",
    "neg": "@SP\nA=M-1\nM=-M\n",
    "eq": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JEQ\nD=0\n@{1}\n0;JMP\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "gt": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JGT\nD=0\n@{1}\n0;JMP\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "lt": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nD=M-D\n@{0}\nD;JLT\nD=0\n@{1}\n0;JMP\n({0})\nD=-1\n({1})\n@SP\nA=M-1\nM=D\n",
    "and": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D&M\n",
    "or": "@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D|M\n",
    "not": "@SP\nA=M-1\nM=!M\n"
}

for k,v in ARITH_TO_ASM.items():
    print("####k=", k)
    if k in ("eq", "gt", "lt"):
        print(v.format("label1", "label2"))
    else:
        print(v)


