; Format: HH:MM:SS.mmm.uuu.nnn
section .data
    format db 27, "[2K", 13, "Time: %02d:%02d:%02d.%03d.%03d.%03d", 13, 0

section .bss
    ms_time resq 1
    us_time resq 1
    ns_time resq 1
    timespec:
        tv_sec  resq 1
        tv_nsec resq 1

section .text
    global main
    extern printf
    extern clock_gettime

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32           ; Increased stack space for alignment

.loop:
    ; Get high-precision time
    mov rax, 228
    mov rdi, 0
    mov rsi, timespec
    syscall

    ; Get nanosecond parts
    mov rax, [timespec + 8]   ; Load nanoseconds
    
    ; Get milliseconds (divide by 1000000)
    mov rdx, 0
    mov rcx, 1000000
    div rcx
    mov [ms_time], rax
    
    ; Get microseconds from remainder (divide by 1000)
    mov rax, rdx
    mov rdx, 0
    mov rcx, 1000
    div rcx
    mov [us_time], rax
    mov [ns_time], rdx        ; Remainder is nanoseconds

    ; Calculate hours
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 3600
    div rcx
    xor rdx, rdx
    mov rcx, 24
    div rcx
    push rdx

    ; Calculate minutes
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 3600
    div rcx
    mov rax, rdx
    xor rdx, rdx
    mov rcx, 60
    div rcx
    push rax

    ; Calculate seconds
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 60
    div rcx

    ; Print time
    mov rdi, format          ; Format string
    pop r8                   ; Get minutes
    pop r9                   ; Get hours
    push rdx                 ; Save seconds
    mov rsi, r9              ; Hours
    mov rdx, r8              ; Minutes
    pop rcx                  ; Seconds
    mov r8, [ms_time]        ; Milliseconds
    mov r9, [us_time]        ; Microseconds
    sub rsp, 8               ; Align stack
    push qword [ns_time]     ; Nanoseconds
    xor eax, eax
    call printf
    add rsp, 16              ; Restore stack

    ; Sleep for 1 nanosecond
    mov rax, 35
    push qword 1
    push qword 0
    mov rdi, rsp
    xor rsi, rsi
    syscall
    add rsp, 16

    jmp .loop

    leave
    ret