/* ═══════════════════════════════════════════════════════════════ */
/* TEZZ-OS — Boot Entry Stub & Hardware Primitives (boot/boot.s)  */
/* ═══════════════════════════════════════════════════════════════ */

.code64

/* ─── Limine Protocol Requests ────────────────────────────────── */

.section .limine_requests, "aw", @progbits
.align 8

.global limine_base_revision
limine_base_revision:
    .quad 0xf9562b2d5c95a6c8
    .quad 0x6a7b384944536bdc
    .quad 3                       /* revision 3 */

.global limine_hhdm_request
limine_hhdm_request:
    .quad 0xc7b1dd30df4c8b88      /* common magic 0 */
    .quad 0x0a82e883a194f07b      /* common magic 1 */
    .quad 0x48dcf1cb8ad2b852      /* hhdm id 0 */
    .quad 0x63984e959a98244b      /* hhdm id 1 */
    .quad 0                       /* revision 0 */
    .quad 0                       /* response pointer (offset 40) */

.global limine_memmap_request
limine_memmap_request:
    .quad 0xc7b1dd30df4c8b88      /* common magic 0 */
    .quad 0x0a82e883a194f07b      /* common magic 1 */
    .quad 0x67cf3d9d378a806f      /* memmap id 0 */
    .quad 0xe304acdfc50c3c62      /* memmap id 1 */
    .quad 0                       /* revision 0 */
    .quad 0                       /* response pointer (offset 40) */

.global limine_kernel_address_request
limine_kernel_address_request:
    .quad 0xc7b1dd30df4c8b88      /* common magic 0 */
    .quad 0x0a82e883a194f07b      /* common magic 1 */
    .quad 0x71ba76863cc55f63      /* kernel address id 0 */
    .quad 0xb2644a48c516a487      /* kernel address id 1 */
    .quad 0                       /* revision 0 */
    .quad 0                       /* response pointer (offset 40) */

.global limine_framebuffer_request
limine_framebuffer_request:
    .quad 0xc7b1dd30df4c8b88      /* common magic 0 */
    .quad 0x0a82e883a194f07b      /* common magic 1 */
    .quad 0x9d5827dcd881dd75      /* fb id 0 */
    .quad 0xa3148604f6fab11b      /* fb id 1 */
    .quad 0                       /* revision 0 */
    .quad 0                       /* response pointer (offset 40) */

.global limine_requests_end
limine_requests_end:
    .quad 0

/* ─── Entry Point ─────────────────────────────────────────────── */

.section .text._tezzos_entry, "ax", @progbits
.global _tezzos_entry
.type _tezzos_entry, @function
_tezzos_entry:
    cli
    cld

    /* Set up stack (128 KB) */
    lea _kstack(%rip), %rsp
    add $131072, %rsp
    and $-16, %rsp

    /* Zero BSS section */
    lea _bss_start(%rip), %rdi
    lea _bss_end(%rip), %rcx
    sub %rdi, %rcx
    xor %eax, %eax
    rep stosb

    /* Populate g_bootinfo */
    /* HHDM */
    movq limine_hhdm_request+40(%rip), %rax
    test %rax, %rax
    jz 1f
    movq 8(%rax), %rdx            /* offset */
    movq %rdx, g_bootinfo+16(%rip) /* hhdm_offset is 3rd field */
1:

    /* MemMap */
    movq limine_memmap_request+40(%rip), %rax
    test %rax, %rax
    jz 2f
    movq 8(%rax), %rdx            /* entry_count */
    movq %rdx, g_bootinfo+0(%rip)  /* memmap_count */
    movq 16(%rax), %rdx           /* entries array pointer */
    movq %rdx, g_bootinfo+8(%rip)  /* memmap_base */
2:

    /* Kernel address */
    movq limine_kernel_address_request+40(%rip), %rax
    test %rax, %rax
    jz 3f
    movq 8(%rax), %rdx            /* phys base */
    movq %rdx, g_bootinfo+24(%rip)
    movq 16(%rax), %rdx           /* virt base */
    movq %rdx, g_bootinfo+32(%rip)
3:

    /* Framebuffer */
    movq limine_framebuffer_request+40(%rip), %rax
    test %rax, %rax
    jz 4f
    cmpq $0, 8(%rax)              /* framebuffer_count */
    jle 4f
    movq 16(%rax), %rdx           /* array of framebuffer pointers */
    movq (%rdx), %rdx             /* first framebuffer pointer */
    test %rdx, %rdx
    jz 4f
    movq 0(%rdx), %rcx            /* address */
    movq %rcx, g_bootinfo+48(%rip)
    movq 8(%rdx), %rcx            /* width */
    movq %rcx, g_bootinfo+56(%rip)
    movq 16(%rdx), %rcx           /* height */
    movq %rcx, g_bootinfo+64(%rip)
    movq 24(%rdx), %rcx           /* pitch */
    movq %rcx, g_bootinfo+72(%rip)
    movzwq 32(%rdx), %rcx         /* bpp */
    movq %rcx, g_bootinfo+80(%rip)
4:

    /* Allocate 32 bytes shadow space for MS ABI call */
    sub $32, %rsp
    /* Call TEZZ-OS kernel main */
    call main
    add $32, %rsp

    /* If main returns, halt the CPU */
.Lhalt:
    cli
    hlt
    jmp .Lhalt

.size _tezzos_entry, . - _tezzos_entry

/* ─── Port I/O Hardware Primitives (MS x64 ABI: RCX=port, RDX=val) ── */

.section .text, "ax", @progbits

.global sys__sys_inb
.global sys_inb
.type sys__sys_inb, @function
.type sys_inb, @function
sys__sys_inb:
sys_inb:
    mov %rcx, %rdx      /* port into %dx */
    xor %rax, %rax
    inb %dx, %al
    ret

.global sys__sys_outb
.global sys_outb
.type sys__sys_outb, @function
.type sys_outb, @function
sys__sys_outb:
sys_outb:
    mov %rdx, %rax      /* val into %al */
    mov %rcx, %rdx      /* port into %dx */
    outb %al, %dx
    xor %eax, %eax
    ret

.global sys__sys_inw
.global sys_inw
.type sys__sys_inw, @function
.type sys_inw, @function
sys__sys_inw:
sys_inw:
    mov %rcx, %rdx      /* port into %dx */
    xor %rax, %rax
    inw %dx, %ax
    ret

.global sys__sys_outw
.global sys_outw
.type sys__sys_outw, @function
.type sys_outw, @function
sys__sys_outw:
sys_outw:
    mov %rdx, %rax      /* val into %ax */
    mov %rcx, %rdx      /* port into %dx */
    outw %ax, %dx
    xor %eax, %eax
    ret

.global sys__sys_inl
.global sys_inl
.type sys__sys_inl, @function
.type sys_inl, @function
sys__sys_inl:
sys_inl:
    mov %rcx, %rdx      /* port into %dx */
    xor %rax, %rax
    inl %dx, %eax
    ret

.global sys__sys_outl
.global sys_outl
.type sys__sys_outl, @function
.type sys_outl, @function
sys__sys_outl:
sys_outl:
    mov %rdx, %rax      /* val into %eax */
    mov %rcx, %rdx      /* port into %dx */
    outl %eax, %dx
    xor %eax, %eax
    ret

/* ─── Framebuffer 32-bit Graphics Primitives (MS x64 ABI) ─────── */

.global fb_put_pixel_32
.global fb__fb_put_pixel_32
.type fb_put_pixel_32, @function
.type fb__fb_put_pixel_32, @function
fb_put_pixel_32:
fb__fb_put_pixel_32:
    /* RCX = addr, RDX = color_32 */
    movl %edx, (%rcx)
    xor %eax, %eax
    ret

.global fb_get_pixel_32
.global fb__fb_get_pixel_32
.type fb_get_pixel_32, @function
.type fb__fb_get_pixel_32, @function
fb_get_pixel_32:
fb__fb_get_pixel_32:
    /* RCX = addr -> EAX = color_32 */
    xor %rax, %rax
    movl (%rcx), %eax
    ret

.global fb_fill_32
.global fb__fb_fill_32
.type fb_fill_32, @function
.type fb__fb_fill_32, @function
fb_fill_32:
fb__fb_fill_32:
    /* RCX = addr, RDX = count_of_pixels, R8 = color_32 */
    push %rdi
    mov %rcx, %rdi
    mov %rdx, %rcx
    mov %r8, %rax
    cld
    rep stosl
    pop %rdi
    xor %eax, %eax
    ret

.global fb_copy_32
.global fb__fb_copy_32
.type fb_copy_32, @function
.type fb__fb_copy_32, @function
fb_copy_32:
fb__fb_copy_32:
    /* RCX = dst, RDX = src, R8 = count_of_pixels */
    push %rdi
    push %rsi
    mov %rcx, %rdi
    mov %rdx, %rsi
    mov %r8, %rcx
    cld
    rep movsl
    pop %rsi
    pop %rdi
    xor %eax, %eax
    ret

/* ─── Hardware Time Stamp Counter (RDTSC) ─────────────────────── */

.global sys_rdtsc
.global sys__sys_rdtsc
.type sys_rdtsc, @function
.type sys__sys_rdtsc, @function
sys_rdtsc:
sys__sys_rdtsc:
    rdtsc
    shlq $32, %rdx
    orq %rdx, %rax
    ret

/* ─── Fast Memory Primitives (MS x64 ABI) ──────────────────────── */

.global sys_memcpy
.global sys__sys_memcpy
.type sys_memcpy, @function
.type sys__sys_memcpy, @function
sys_memcpy:
sys__sys_memcpy:
    /* RCX = dst, RDX = src, R8 = bytes */
    push %rdi
    push %rsi
    mov %rcx, %rdi
    mov %rdx, %rsi
    mov %r8, %rcx
    cld
    rep movsb
    pop %rsi
    pop %rdi
    xor %eax, %eax
    ret

.global sys_memset
.global sys__sys_memset
.type sys_memset, @function
.type sys__sys_memset, @function
sys_memset:
sys__sys_memset:
    /* RCX = dst, RDX = val, R8 = bytes */
    push %rdi
    mov %rcx, %rdi
    mov %rdx, %rax
    mov %r8, %rcx
    cld
    rep stosb
    pop %rdi
    xor %eax, %eax
    ret

/* ─── CPUID Hardware Primitive (MS x64 ABI: RCX=leaf, RDX=subleaf, R8=regs) ── */

.global sys_cpuid
.global sys__sys_cpuid
.type sys_cpuid, @function
.type sys__sys_cpuid, @function
sys_cpuid:
sys__sys_cpuid:
    push %rbx
    push %rdi
    mov %r8, %rdi
    mov %rcx, %rax
    mov %rdx, %rcx
    cpuid
    /* Zero-extend 32-bit registers into 64-bit ints at 8-byte offsets */
    mov %eax, %eax
    movq %rax, 0(%rdi)
    mov %ebx, %ebx
    movq %rbx, 8(%rdi)
    mov %ecx, %ecx
    movq %rcx, 16(%rdi)
    mov %edx, %edx
    movq %rdx, 24(%rdi)
    pop %rdi
    pop %rbx
    xor %eax, %eax
    ret



