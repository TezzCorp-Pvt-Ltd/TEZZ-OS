/* TEZZ-OS Linker Script — x86_64 ELF kernel */
/* Targets the Limine boot protocol (higher-half kernel at 0xFFFFFFFF80000000) */

OUTPUT_FORMAT("elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_tezzos_entry)

PHDRS
{
    text    PT_LOAD FLAGS(5);   /* r-x */
    rodata  PT_LOAD FLAGS(4);   /* r-- */
    data    PT_LOAD FLAGS(6);   /* rw- */
    bss     PT_LOAD FLAGS(6);   /* rw- */
}

SECTIONS
{
    /* Higher-half kernel base: -2GB virtual offset */
    . = 0xFFFFFFFF80000000;

    /* ------ Text (code) section ------ */
    .text ALIGN(4096) : AT(ADDR(.text) - 0xFFFFFFFF80000000)
    {
        _kernel_start = .;
        KEEP(*(.limine_requests))      /* Limine protocol requests */
        *(.text._tezzos_entry)         /* Entry point first */
        *(.text*)
    } :text

    /* ------ Read-only data ------ */
    .rodata ALIGN(4096) : AT(ADDR(.rodata) - 0xFFFFFFFF80000000)
    {
        *(.rodata*)
        *(.limine_reqs*)
    } :rodata

    /* ------ Initialized data ------ */
    .data ALIGN(4096) : AT(ADDR(.data) - 0xFFFFFFFF80000000)
    {
        *(.data*)
    } :data

    /* ------ Uninitialized data ------ */
    .bss ALIGN(4096) : AT(ADDR(.bss) - 0xFFFFFFFF80000000)
    {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        _bss_end = .;
    } :bss

    _kernel_end = .;

    /* Discard debug/unneeded sections */
    /DISCARD/ :
    {
        *(.note*)
        *(.comment*)
        *(.eh_frame*)
    }
}
