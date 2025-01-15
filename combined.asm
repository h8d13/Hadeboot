section .data
    format db 27, "[2K", 13, "T: %s:%s:%s.%03s.%03s.%03s", 13, 0
section .bss
    ms_time   resq 1
    us_time   resq 1
    ns_time   resq 1
    timespec:
        tv_sec  resq 1
        tv_nsec resq 1
    ternary_hours   resb 32
    ternary_minutes resb 32
    ternary_seconds resb 32
    ternary_ms      resb 32
    ternary_us      resb 32
    ternary_ns      resb 32
section .text
    global _start
    extern printf

; Balanced ternary conversion function
to_balanced_ternary:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi        ; number to convert
    mov r13, rsi        ; buffer
    xor r14, r14        ; position

.convert_loop:
    mov rax, r12
    xor rdx, rdx
    mov rcx, 3
    div rcx
    
    ; Adjust for balanced ternary representation
    cmp rdx, 2
    jl .handle_normal
    
    ; If remainder is 2, we need to carry over and subtract
    inc rax             ; Carry over
    mov dl, '-'         ; Represents -1
    jmp .store_digit

.handle_normal:
    cmp rdx, 1
    je .positive
    mov dl, '0'
    jmp .store_digit

.positive:
    mov dl, '+'         ; Represents +1

.store_digit:
    mov [r13 + r14], dl
    inc r14
    
    mov r12, rax        ; Update number for next iteration
    
    test r12, r12
    jnz .convert_loop
    
    mov byte [r13 + r14], 0   ; null terminate
    
    ; In-place string reversal
    dec r14
    xor r8, r8
.reverse:
    cmp r8, r14
    jge .done
    
    mov al, [r13 + r8]
    xchg al, [r13 + r14]
    mov [r13 + r8], al
    
    inc r8
    dec r14
    jmp .reverse
    
.done:
    pop r14
    pop r13
    pop r12
    pop rbp
    ret

_start:
    push rbp
    mov rbp, rsp
    sub rsp, 64
.loop:
    ; Get high-precision time via syscall
    xor rdi, rdi
    mov rax, 228        ; clock_gettime syscall
    mov rsi, timespec
    syscall
    ; Calculate time components
    mov rax, [timespec + 8]   ; nanoseconds
    xor rdx, rdx
    mov rcx, 1000000
    div rcx
    mov [ms_time], rax
    
    mov rax, rdx
    xor rdx, rdx
    mov rcx, 1000
    div rcx
    mov [us_time], rax
    mov [ns_time], rdx
    ; Convert time components to balanced ternary
    mov rax, [timespec]
    mov rcx, 3600
    xor rdx, rdx
    div rcx
    xor rdx, rdx
    mov rcx, 24
    div rcx
    mov rdi, rdx        ; hours
    mov rsi, ternary_hours
    call to_balanced_ternary
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 3600
    div rcx
    mov rax, rdx
    xor rdx, rdx
    mov rcx, 60
    div rcx
    mov rdi, rax        ; minutes
    mov rsi, ternary_minutes
    call to_balanced_ternary
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 60
    div rcx
    mov rdi, rdx        ; seconds
    mov rsi, ternary_seconds
    call to_balanced_ternary
    ; Convert time precision components
    mov rdi, [ms_time]
    mov rsi, ternary_ms
    call to_balanced_ternary
    mov rdi, [us_time]
    mov rsi, ternary_us
    call to_balanced_ternary
    mov rdi, [ns_time]
    mov rsi, ternary_ns
    call to_balanced_ternary
    ; Print formatted time
    mov rdi, format
    mov rsi, ternary_hours
    mov rdx, ternary_minutes
    mov rcx, ternary_seconds
    mov r8, ternary_ms
    mov r9, ternary_us
    push qword ternary_ns
    xor rax, rax
    call printf
    add rsp, 8
    ; Minimal sleep to control loop
    mov rax, 35         ; nanosleep syscall
    push qword 1
    push qword 0
    mov rdi, rsp
    xor rsi, rsi
    syscall
    add rsp, 16
    
    jmp .loop
    ; Unreachable exit (for completeness)
    mov rax, 60
    xor rdi, rdi
    syscall