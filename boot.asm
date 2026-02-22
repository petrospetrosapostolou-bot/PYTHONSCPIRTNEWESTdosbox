BITS 16

ORG 0x7C00  ; Origin at the boot sector

start:
    ; Your bootloader code here
    mov ax, 0x0000  ; Set up the data segment
    mov ds, ax

    ; Add your bootloader logic here
    mov si, msg   ; Load the address of msg into SI
    call print_string  ; Call the function to print

    jmp $  ; Loop forever; $ is the current address

msg db 'Hello, World! Press any key to reboot...', 0

; Print a string function
print_string:
    ; Function to print a string pointed by SI
    mov ah, 0x0E  ; BIOS teletype function
.next_char:
    lodsb        ; Load byte at DS:SI into AL and increment SI
    cmp al, 0    ; Check if we reached the end of string
    je .done     ; If end, jump to done
    int 0x10     ; Print the character in AL
    jmp .next_char  ; Loop back for next char
.done:
    ret

times 510 - ($ - $$) db 0 ; Fill the rest of the sector with 0
 dw 0xAA55 ; Boot signature