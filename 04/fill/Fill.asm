// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

    // set @curr_ptr to start address of @SCREEN
    @SCREEN
    D=A             
    @curr_ptr
    M=D             
    
    // set @max_ptr to last address of @SCREEN
    @8192
    D=D+A
    @max_ptr
    M=D

(CHECKSTATE)
    // determine if a key was pressed
    @KBD
    D=M

    // if not, make screen white
    @WHITEOUT
    D;JEQ

    // otherwise, make it black
    @BLACKOUT
    0;JMP

// color @curr_ptr address
(BLACKOUT)
    @curr_ptr
    A=M
    M=-1
    @FILLSCREEN
    0;JMP

(WHITEOUT)
    @curr_ptr
    A=M
    M=0
    @FILLSCREEN
    0;JMP

(FILLSCREEN)
    // move @curr_ptr to next address
    @curr_ptr
    D=M+1
    M=D

    // check how many pixels left
    @max_ptr
    D=D-M

    // if we're not at the end, keep going
    @CHECKSTATE
    D;JNE

    // otherwise move @curr_ptr back to start
    @SCREEN
    D=A
    @curr_ptr
    M=D

    // and then keep going
    @CHECKSTATE
    0;JMP
