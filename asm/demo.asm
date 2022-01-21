serialdata   equ    0xf001    ; IO address for serial data
serialstatus equ    0xf000    ; IO address for serial status

mov r14, 0xf000      ; set stack pointer
mov r1, message      ; R1 = pointer to message string
call printstring     ; print string
keyloop:
call waitkey         ; wait for rx data to be available
call readkey         ; read key press
call sendchar        ; write key code to serial terminal
bra keyloop          ; wait for next key

waitkey:
ldb r0, serialstatus ; read for serial status
cp r0, 1             ; is there RX data available?
bnz waitkey          ; if not keep waiting
ret

readkey:
ldb r0, serialdata   ; read key from serial port
ret

sendchar:
stb serialdata, r0   ; write character to serial port
cp r0, 0xd           ; is character CR?
bnz senddone         ; if it wasn't we are done
mov r0, 0x0a         ; R0 = LF
stb serialdata, r0   ; write LF character to serial port
senddone:
ret


printstring:
and r0,r0            ; clear carry bit
sub r14, 2           ; subtrace 2 from stack pointer
stw @r14, r15        ; put return addres on stack
loop1:
ldb r0, @r1          ; R0 = character pointed to by r1
cp r0, 0x00          ; is the current character NULL?
bz printdone         ; if so then we are done
call sendchar        ; send character to serial port
and r0, r0           ; clear carry bit
add r1, 1            ; increment pointer
bra loop1            ; print next character
printdone:
ldw r15, @r14        ; get stored return address from stack
and r0,r0            ; clear carry bit
add r14, 2           ; add 2 to stack pointer
ret

message:
defb 0x43, 0x50, 0x55, 0x20, 0x44, 0x65, 0x6d, 0x6f, 0x0d, 0x00 ; CPU Demo
