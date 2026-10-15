# TEZZ-OS — Master Build Plan & Roadmap

> **Pure TezzNative OS Kernel** — Custom higher-half 64-bit operating system with Linear Framebuffer graphics, VFS, package manager, superuser permissions, and comprehensive hardware discovery. Zero Linux dependencies.

---

## Directory Layout

```
c:\Acer\Code\TEZZ-OS\
├── kernel/
│   ├── main.tn       ← Kernel entry, boot sequence, boot banner, kmain()
│   ├── gdt.tn        ← Global Descriptor Table wrapper
│   ├── idt.tn        ← IDT + exception/IRQ wiring
│   ├── pic.tn        ← 8259A PIC remap and control
│   ├── pit.tn        ← PIT 8253 timer (1000 Hz)
│   ├── pmem.tn       ← Physical memory bitmap allocator
│   ├── vmem.tn       ← x86_64 4-level virtual memory / paging
│   ├── heap.tn       ← Kernel heap (first-fit, coalescing, 16-byte aligned)
│   ├── proc.tn       ← Process manager (Phase 1 stub)
│   ├── syscall.tn    ← System call table (Phase 1 stub)
│   └── panic.tn      ← Kernel panic / assert
│
├── drivers/
│   ├── vga.tn        ← VGA text mode 80×25, 16 colors, cursor, scroll
│   ├── keyboard.tn   ← PS/2 keyboard: full scancode set 1, modifiers, IRQ1
│   ├── mouse.tn      ← PS/2 mouse: 3/4-byte packets, IntelliMouse, IRQ12
│   └── serial.tn     ← COM1 serial debug output (115200 baud)
│
├── shell/
│   └── shell.tn      ← Interactive CLI shell (full line editor + commands)
│
├── fs/               ← Reserved for Phase 2 filesystem drivers
├── boot/
│   └── limine.cfg    ← Limine bootloader configuration
├── tools/
│   └── linker.ld     ← x86_64 ELF higher-half linker script
│
├── build.ps1         ← Windows build script
├── build.sh          ← Linux/macOS/WSL build script
├── tezz.mod          ← TezzNative module definition
└── docs/             ← Reserved for API documentation
```

---

## How to Build

### Windows (PowerShell)
```powershell
cd c:\Acer\Code\TEZZ-OS

# Compile kernel ELF only
.\build.ps1

# Compile + create bootable ISO
.\build.ps1 -Iso

# Compile + ISO + launch in QEMU
.\build.ps1 -Iso -Run

# Custom tezzc path
.\build.ps1 -TezzC "C:\path\to\tezzc.exe" -Iso -Run
```

### Linux / WSL
```bash
cd /path/to/TEZZ-OS
chmod +x build.sh

./build.sh           # ELF only
./build.sh --iso     # + bootable ISO
./build.sh --iso --run  # + QEMU
```

### Direct compile (manual)
```bash
tezzc buildexe --target=x86_64-bare kernel/main.tn build/tezzos.elf
```

---

## Requirements

| Tool | Purpose |
|------|---------|
| `tezzc` (TezzNative compiler) | Compiles `.tn` files to ELF |
| `xorriso` | Creates bootable ISO |
| `limine` | Bootloader (auto-downloaded) |
| `qemu-system-x86_64` | Virtual machine for testing |

---

## Phase 1 Shell Commands (All Implemented)

| Command | Description |
|---------|-------------|
| `help` | List all commands and keyboard shortcuts |
| `clear` | Clear the screen |
| `echo [text]` | Print text to console |
| `version` | Show OS version and build info |
| `mem` | Memory usage with ASCII bar chart |
| `uptime` | System uptime in h/m/s |
| `cpuid` | CPU vendor and architecture info |
| `proc` | List running processes |
| `color [0-4]` | Change color scheme (default/matrix/amber/cyan/classic) |
| `history` | Show command history (last 50 entries) |
| `neofetch` | System info display with ASCII art logo |
| `reboot` | Reboot via PS/2 controller reset |
| `shutdown` | Power off via ACPI (QEMU/VirtualBox) |

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate command history |
| `←` / `→` | Move cursor in input line |
| `Home` / `End` | Jump to start/end of line |
| `Del` | Delete character at cursor |
| `Backspace` | Delete character before cursor |
| `Tab` | Auto-complete command name |
| `Esc` | Clear current input line |
| `Ctrl+L` | Clear screen |
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Shutdown |
| `F1–F12` | Reserved for future commands |

### Mouse / Touchpad Support
| Action | Effect |
|--------|--------|
| Move | Moves cursor block visible on screen |
| Left click | Positions shell cursor at clicked column |
| Scroll wheel | Scrolls terminal output (Phase 2 full impl) |

---

## Boot Sequence

```
UEFI/BIOS → Limine Bootloader
    ↓
_tezzos_entry()          [ELF entry point]
    ↓
bss_clear()              [zero BSS segment]
    ↓
serial.init(115200)      [debug output]
    ↓
vga.init() + clear()     [text console]
    ↓
boot_banner()            [TezzOS ASCII art]
    ↓
hardware_init():
  gdt.init()             [load GDT]
  idt.init()             [load IDT + wire IRQs]
  pic.init() + remap()   [8259A remapping]
  pit.init(1000)         [1000Hz timer]
  pmem.init()            [physical memory map]
  vmem.init()            [4-level paging]
  heap.init(4MB)         [kernel heap]
  syscall.init()         [syscall table]
  proc.init()            [process table]
  keyboard.init()        [PS/2 keyboard]
  mouse.init()           [PS/2 mouse]
  kernel.sti()           [enable interrupts]
    ↓
shell.run()              [interactive CLI loop]
```

---

## 5-Phase Roadmap

### ✅ Phase 1 — CLI Kernel (CURRENT)
**Goal:** A working, interactive OS kernel with keyboard + mouse support.

- [x] GDT, IDT, PIC, PIT
- [x] Physical memory manager
- [x] Virtual memory (4-level paging)
- [x] Kernel heap allocator
- [x] VGA text mode driver (80×25, 16 colors, cursor, scroll)
- [x] PS/2 keyboard (full scancode set 1, all modifiers, F1–F12, arrows)
- [x] PS/2 mouse (3/4-byte packets, IntelliMouse scroll, cursor visual)
- [x] Serial debug (COM1 @ 115200)
- [x] Interactive CLI shell (line editor, history, tab-complete, 13 commands)
- [x] Boot banner with ASCII art

---

### 🔄 Phase 2 — Userspace & Filesystem (3–4 months)
**Goal:** Run programs. Store files. Basic POSIX subset.

- [ ] Context switch assembly stubs (x86_64 `cpu_context_switch`)
- [ ] Preemptive process scheduler (using kernel.tn `proc_schedule`)
- [ ] ELF userspace loader (ring-3 processes, separate page tables)
- [ ] POSIX syscall handlers: `read`, `write`, `open`, `close`, `fork`, `exec`, `wait`
- [ ] FAT32 filesystem driver (using `kernel.tn` VfsOps interface)
- [ ] IDE/AHCI ATA block device driver
- [ ] `ls`, `cat`, `cd`, `mkdir`, `rm` shell commands
- [ ] RAM disk (initrd) support
- [ ] Shell piping (`cmd1 | cmd2`)

---

### 🔄 Phase 3 — Networking & SMP (6–12 months)
**Goal:** Network capability. Multi-core support.

- [ ] NE2000/RTL8139/e1000 Ethernet driver (via PCI)
- [ ] TCP/IP stack (using `net.tn` as a foundation)
- [ ] UDP socket interface
- [ ] DHCP client
- [ ] HTTP GET (minimal browser)
- [ ] SMP bring-up (APIC IPI + per-CPU stacks)
- [ ] Multi-core process scheduling

---

### 🔄 Phase 4 — Security & Stability (12–18 months)
**Goal:** A kernel you can actually trust.

- [ ] ASLR (address space layout randomization)
- [ ] Guard pages (null pointer + stack overflow protection)
- [ ] Capability-based security model
- [ ] seccomp-style syscall filtering
- [ ] Kernel hardening (`-fstack-protector`, stack canaries in TezzNative)
- [ ] ext2 filesystem driver
- [ ] ACPI power management (proper shutdown, suspend)

---

### 🔄 Phase 5 — AI-Native OS (18–36 months)
**Goal:** The kernel Linux cannot be.

- [ ] NPU/GPU first-class scheduling (`npu.tn`, `gpu.tn`)
- [ ] Tensor memory management (zero-copy model loading)
- [ ] AI priority queue in process scheduler
- [ ] `nn.tn` / `llm_core.tn` integrated as kernel services
- [ ] Real-time scheduling guarantees (< 100µs latency target)
- [ ] ARM64 / RISC-V ports
- [ ] TezzNative userspace programs as first-class apps

---

## Testing in QEMU

```powershell
# Quick test (no ISO needed):
qemu-system-x86_64 -machine q35 -cpu qemu64 -m 256M `
    -serial stdio -vga std `
    -kernel build\tezzos.elf

# With full boot ISO:
qemu-system-x86_64 -machine q35 -cpu qemu64 -m 256M `
    -serial stdio -vga std `
    -cdrom build\tezzos.iso -boot d
```

**QEMU Serial output** will show all `serial.log()` messages in your terminal.
**VGA output** appears in the QEMU window showing the full TezzOS UI.

---

## Kernel Parameters (cmdline)

Pass via `limine.cfg`:
```
CMDLINE=console=vga0 debug=serial verbose=1
```

| Parameter | Effect |
|-----------|--------|
| `console=vga0` | VGA text console (default) |
| `debug=serial` | Enable serial debug output |
| `verbose=1` | Verbose boot messages |

---

## Contributing / Next Steps

1. **Implement context switch** — `kernel/proc.tn` Phase 2 scheduler
2. **Write FAT32 driver** — `fs/fat32.tn` implementing `VfsOps`
3. **Test on real hardware** — Burn ISO to USB with Rufus/dd, boot on x86_64 PC
4. **Add more shell commands** — `ls`, `cat`, `date`, `env`
5. **Port to ARM64** — Raspberry Pi target using `raspi.tn`
