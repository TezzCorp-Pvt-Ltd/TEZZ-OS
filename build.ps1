# ???????????????????????????????????????????????????????????????
# TEZZ-OS Build & Run Automation Script
# Run from: c:\Acer\Code\TEZZ-OS
# ???????????????????????????????????????????????????????????????

param(
    [string]$TezzC  = "..\TezzNative\tezzc.exe",
    [switch]$Iso = $true,
    [switch]$Run
)

$ErrorActionPreference = "Continue"
$BUILD_DIR = ".\build"

Write-Host ""
Write-Host "  +------------------------------------------+" -ForegroundColor Cyan
Write-Host "  |   TEZZ-OS Operating System Build 0.1.0   |" -ForegroundColor Cyan
Write-Host "  +------------------------------------------+" -ForegroundColor Cyan
Write-Host ""

# Ensure build dir exists
if (-not (Test-Path $BUILD_DIR)) {
    New-Item -ItemType Directory -Path $BUILD_DIR | Out-Null
}

# Locate tools
$Clang = "clang"
if (Test-Path "C:\msys64\clangarm64\bin\clang.exe") {
    $Clang = "C:\msys64\clangarm64\bin\clang.exe"
}
$Lld = "lld"
if (Test-Path "C:\msys64\clangarm64\bin\ld.lld.exe") {
    $Lld = "C:\msys64\clangarm64\bin\ld.lld.exe"
}
$Xorriso = "xorriso"
if (Test-Path "C:\msys64\usr\bin\xorriso.exe") {
    $Xorriso = "C:\msys64\usr\bin\xorriso.exe"
}
$Limine = "tools\limine\limine.exe"
$Qemu = "qemu-system-x86_64"
if (Test-Path "C:\msys64\clangarm64\bin\qemu-system-x86_64.exe") {
    $Qemu = "C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
}

# Check tezzc
if (-not (Test-Path $TezzC)) {
    Write-Host "  [ERROR] tezzc not found at: $TezzC" -ForegroundColor Red
    exit 1
}

Write-Host "  [1/5] Compiling assembly boot stubs..." -ForegroundColor White
& $Clang --target=x86_64-unknown-none-elf -c boot\boot.s -o "$BUILD_DIR\boot.o"
& $Clang --target=x86_64-unknown-none-elf -c boot\font.s -o "$BUILD_DIR\font.o"
Write-Host "  [1/5] OK - boot.o, font.o" -ForegroundColor Green

Write-Host "  [2/5] Compiling kernel in Pure TezzNative..." -ForegroundColor White
& $TezzC buildir kernel\main.tn "$BUILD_DIR\tezzos.s" --freestanding
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] TezzNative compilation failed." -ForegroundColor Red
    exit 1
}
& $Clang --target=x86_64-unknown-none-elf -c "$BUILD_DIR\tezzos.s" -o "$BUILD_DIR\tezzos.o"
Write-Host "  [2/5] OK - tezzos.o" -ForegroundColor Green

Write-Host "  [3/5] Linking higher-half ELF kernel..." -ForegroundColor White
& $Lld -flavor gnu -m elf_x86_64 -T tools\linker.ld "$BUILD_DIR\boot.o" "$BUILD_DIR\font.o" "$BUILD_DIR\tezzos.o" -o "$BUILD_DIR\tezzos.elf"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] Linking failed." -ForegroundColor Red
    exit 1
}
Write-Host "  [3/5] OK - tezzos.elf" -ForegroundColor Green

if ($Iso) {
    Write-Host "  [4/5] Packaging bootable Limine ISO..." -ForegroundColor White

    $ISO_DIR = "$BUILD_DIR\iso_root"
    $BOOT_DIR = "$ISO_DIR\boot"
    $LIMINE_DIR = "$BOOT_DIR\limine"
    $EFI_DIR = "$ISO_DIR\EFI"
    $EFI_BOOT_DIR = "$EFI_DIR\BOOT"

    New-Item -ItemType Directory -Path $LIMINE_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path $EFI_BOOT_DIR -Force | Out-Null

    # Boot configuration files
    Copy-Item "boot\limine.cfg" "$ISO_DIR\limine.cfg" -Force
    Copy-Item "boot\limine.cfg" "$ISO_DIR\limine.conf" -Force
    Copy-Item "boot\limine.cfg" "$LIMINE_DIR\limine.cfg" -Force
    Copy-Item "boot\limine.cfg" "$LIMINE_DIR\limine.conf" -Force
    Copy-Item "boot\limine.cfg" "$EFI_BOOT_DIR\limine.conf" -Force

    # Kernel ELF binary in both standard search paths
    Copy-Item "$BUILD_DIR\tezzos.elf" "$BOOT_DIR\tezzos.elf" -Force
    Copy-Item "$BUILD_DIR\tezzos.elf" "$ISO_DIR\tezzos.elf" -Force

    # Vendor EFI binaries for bare-metal UEFI booting
    if (Test-Path "tools\limine\BOOTX64.EFI") {
        Copy-Item "tools\limine\BOOTX64.EFI" "$EFI_BOOT_DIR\" -Force
        Copy-Item "tools\limine\BOOTX64.EFI" "$LIMINE_DIR\" -Force
    }
    if (Test-Path "tools\limine\BOOTIA32.EFI") {
        Copy-Item "tools\limine\BOOTIA32.EFI" "$EFI_BOOT_DIR\" -Force
    }
    if (Test-Path "tools\limine\BOOTAA64.EFI") {
        Copy-Item "tools\limine\BOOTAA64.EFI" "$EFI_BOOT_DIR\" -Force
    }

    # Vendor BIOS binaries for legacy BIOS booting
    Copy-Item "tools\limine\limine-bios.sys" "$LIMINE_DIR\" -Force
    Copy-Item "tools\limine\limine-bios-cd.bin" "$LIMINE_DIR\" -Force
    Copy-Item "tools\limine\limine-uefi-cd.bin" "$LIMINE_DIR\" -Force

    $iso_args = @(
        "-as", "mkisofs",
        "-b", "boot/limine/limine-bios-cd.bin",
        "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
        "--efi-boot", "boot/limine/limine-uefi-cd.bin",
        "-efi-boot-part", "--efi-boot-image",
        "--protective-msdos-label",
        $ISO_DIR,
        "-o", "$BUILD_DIR\tezzos.iso"
    )
    & $Xorriso @iso_args 2>&1 | Out-Null
    & $Limine bios-install "$BUILD_DIR\tezzos.iso" 2>&1 | Out-Null

    Write-Host "  [4/5] OK - tezzos.iso (Dual UEFI + BIOS Hybrid)" -ForegroundColor Green
}

Write-Host "  [5/5] Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Kernel: $BUILD_DIR\tezzos.elf" -ForegroundColor Cyan
Write-Host "  ISO:    $BUILD_DIR\tezzos.iso" -ForegroundColor Cyan
Write-Host ""

if ($Run) {
    Write-Host "  Launching QEMU (1280x800 Framebuffer + Dual Serial COM1)..." -ForegroundColor Yellow
    Write-Host ""

    $qemu_args = @(
        "-machine", "q35",
        "-cpu", "qemu64",
        "-m", "256M",
        "-cdrom", "$BUILD_DIR\tezzos.iso",
        "-boot", "d",
        "-serial", "stdio",
        "-vga", "std"
    )

    & $Qemu @qemu_args
}
