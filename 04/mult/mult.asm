// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    @1
    D=M    // D<-R1
    @count
    M=D    // M[count]<-R1
    @2
    M=0    // R2<-0
(LOOP)
    @count
    D=M    // D=count
    @END
    D;JEQ  // if count=0 goto END
    @1
    D=D-A  // D<-count-1
    @count
    M=D    // M[count]<-D
    @2
    D=M    // D<-R2
    @0
    D=D+M  // D<-D+R0
    @2
    M=D    // R2<-D
    @LOOP
    0;JMP  // Goto LOOP
(END)
    @END
    0;JMP  // Infinite loop