section .data
    format db 27, "[2K", 13, "T: %s:%s:%s.%s.%s.%s", 13, 0
    
section .bss
    ms_time resq 1
    us_time resq 1
    ns_time resq 1
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

; Optimized balanced ternary conversion
to_balanced_ternary:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    push r14
    
    mov r12, rdi        ; number to convert
    mov r13, rsi        ; buffer
    xor r14, r14        ; position (faster than mov)
.convert_loop:
    ; Fast division by 3
    mov rax, r12
    xor rdx, rdx
    mov rcx, 3
    div rcx
    
    mov r12, rax        ; quotient for next iteration
    
    ; Combine remainder conversion and storing
    add dl, '0'         
    mov [r13 + r14], dl
    inc r14
    
    test r12, r12       ; faster than cmp
    jnz .convert_loop
    
    mov byte [r13 + r14], 0   ; null terminate
    
    ; Optimized in-place reversal
    dec r14             ; last index
    xor r8, r8          ; start index
.reverse:
    cmp r8, r14
    jge .done
    
    ; Single-pass swap with fewer moves
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
    ; Minimize syscall setup
    xor rdi, rdi        ; faster than mov
    mov rax, 228        ; clock_gettime syscall
    mov rsi, timespec
    syscall

    ; Combine divisions with fewer register moves
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

    ; Time component extractions with minimal instructions
    mov rax, [timespec]
    mov rcx, 3600
    xor rdx, rdx
    div rcx             ; hours and remainder
    xor rdx, rdx
    mov rcx, 24
    div rcx
    mov rdi, rdx        ; hours
    mov rsi, ternary_hours
    call to_balanced_ternary

    ; Repeated time division pattern
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

    ; Seconds extraction
    mov rax, [timespec]
    xor rdx, rdx
    mov rcx, 60
    div rcx
    mov rdi, rdx        ; seconds
    mov rsi, ternary_seconds
    call to_balanced_ternary

    ; Conversions with direct memory access
    mov rdi, [ms_time]
    mov rsi, ternary_ms
    call to_balanced_ternary

    mov rdi, [us_time]
    mov rsi, ternary_us
    call to_balanced_ternary

    mov rdi, [ns_time]
    mov rsi, ternary_ns
    call to_balanced_ternary

    ; Optimized printf setup
    mov rdi, format
    mov rsi, ternary_hours
    mov rdx, ternary_minutes
    mov rcx, ternary_seconds
    mov r8, ternary_ms
    mov r9, ternary_us
    push qword ternary_ns
    xor rax, rax        ; faster than mov
    call printf
    add rsp, 8

    ; Minimal sleep overhead
    mov rax, 35         ; nanosleep syscall
    push qword 1        ; consistent sleep duration
    push qword 0
    mov rdi, rsp
    xor rsi, rsi
    syscall
    add rsp, 16
    
    jmp .loop
    mov rax, 60         ; exit syscall (unreachable)
    xor rdi, rdi
    syscall