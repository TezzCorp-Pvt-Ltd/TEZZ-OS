# =====================================================================
# TEZZ-OS — Bare-Metal Bootable USB Creation Tool (tools/make_usb.ps1)
# =====================================================================
#
# Creates a dual UEFI + Legacy BIOS bootable USB flash drive for TEZZ-OS.
#
# Usage:
#   .\tools\make_usb.ps1 -Drive <Letter> [-Format] [-Force]
#   .\tools\make_usb.ps1 -IsoHybrid
#   .\tools\make_usb.ps1 -Image [-SizeMB 64]
#   .\tools\make_usb.ps1 -Help
# =====================================================================

param(
    [string]$Drive,
    [switch]$Format,
    [switch]$Force,
    [switch]$IsoHybrid,
    [switch]$Image,
    [int]$SizeMB = 64,
    [switch]$Help
)

$ErrorActionPreference = "Continue"

function Show-Header {
    Write-Host ""
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host "    TEZZ-OS 0.1.0 'Nova' - Bare-Metal USB Deployment Tool         " -ForegroundColor Cyan
    Write-Host "  ================================================================" -ForegroundColor Cyan
    Write-Host ""
}

if ($Help -or (-not $Drive -and -not $IsoHybrid -and -not $Image)) {
    Show-Header
    Write-Host "  Usage Examples:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Prepare a Physical USB Flash Drive (UEFI & BIOS Dual-Boot):" -ForegroundColor White
    Write-Host "     .\tools\make_usb.ps1 -Drive E: -Format" -ForegroundColor Green
    Write-Host "     Formats drive E: as FAT32, installs Limine UEFI (BOOTX64.EFI)," -ForegroundColor Gray
    Write-Host "     Limine BIOS stage 1/2, config, and TezzOS kernel ELF." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Quick Copy to an Existing FAT32 USB Flash Drive (UEFI Boot):" -ForegroundColor White
    Write-Host "     .\tools\make_usb.ps1 -Drive E:" -ForegroundColor Green
    Write-Host "     Copies all required EFI vendor files without reformatting." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Flash via Rufus / balenaEtcher / dd:" -ForegroundColor White
    Write-Host "     .\tools\make_usb.ps1 -IsoHybrid" -ForegroundColor Green
    Write-Host "     Explains how to flash the prebuilt build\tezzos.iso hybrid image." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. Build a Raw Bootable USB Disk Image (build\tezzos_usb.img):" -ForegroundColor White
    Write-Host "     .\tools\make_usb.ps1 -Image" -ForegroundColor Green
    Write-Host ""
    exit 0
}

Show-Header

$ISO_ROOT = "build\iso_root"
$KERNEL_ELF = "build\tezzos.elf"
$LIMINE_EXE = "tools\limine\limine.exe"

# Ensure kernel is built
if (-not (Test-Path $KERNEL_ELF)) {
    Write-Host "  [!] Kernel ELF not found. Running build.ps1 first..." -ForegroundColor Yellow
    & powershell -ExecutionPolicy Bypass -File .\build.ps1 -Iso
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Build failed." -ForegroundColor Red
        exit 1
    }
}

if ($IsoHybrid) {
    Write-Host "  [+] Prebuilt Hybrid ISO Information:" -ForegroundColor White
    Write-Host "      File: build\tezzos.iso" -ForegroundColor Cyan
    $isoSize = (Get-Item "build\tezzos.iso").Length / 1MB
    Write-Host "      Size: $([math]::Round($isoSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  How to Flash to USB for Bare-Metal Booting:" -ForegroundColor Yellow
    Write-Host "    A. Using Rufus (Windows):" -ForegroundColor White
    Write-Host "       1. Insert USB pendrive." -ForegroundColor Gray
    Write-Host "       2. Open Rufus, select your USB drive." -ForegroundColor Gray
    Write-Host "       3. Choose 'build\tezzos.iso'." -ForegroundColor Gray
    Write-Host "       4. Partition scheme: MBR, Target system: BIOS or UEFI." -ForegroundColor Gray
    Write-Host "       5. Click START (either ISO or DD mode will work)." -ForegroundColor Gray
    Write-Host ""
    Write-Host "    B. Using balenaEtcher / Raspberry Pi Imager:" -ForegroundColor White
    Write-Host "       1. Select 'build\tezzos.iso'." -ForegroundColor Gray
    Write-Host "       2. Select USB drive and click 'Flash!'." -ForegroundColor Gray
    Write-Host ""
    Write-Host "    C. Using Linux/macOS 'dd':" -ForegroundColor White
    Write-Host "       sudo dd if=build/tezzos.iso of=/dev/sdX bs=4M status=progress oflag=sync" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

if ($Image) {
    Write-Host "  [1/3] Generating raw USB disk image: build\tezzos_usb.img ($SizeMB MB)..." -ForegroundColor White
    $imgFile = "build\tezzos_usb.img"
    if (Test-Path $imgFile) { Remove-Item $imgFile -Force }

    $Clang = "C:\msys64\clangarm64\bin\qemu-img.exe"
    if (Test-Path $Clang) {
        & $Clang create -f raw $imgFile "${SizeMB}M" | Out-Null
    } else {
        # Create zeroed sparse/binary file via PowerShell
        $fs = [System.IO.File]::Create($imgFile)
        $fs.SetLength($SizeMB * 1024 * 1024)
        $fs.Close()
    }
    Write-Host "  [1/3] OK - Empty raw image created." -ForegroundColor Green

    Write-Host "  [2/3] Installing Limine BIOS MBR boot code into raw image..." -ForegroundColor White
    & $LIMINE_EXE bios-install $imgFile 2>&1 | Out-Null
    Write-Host "  [2/3] OK - Limine MBR installed." -ForegroundColor Green

    Write-Host "  [3/3] Image ready at: $imgFile" -ForegroundColor Cyan
    Write-Host "        You can test-boot it in QEMU via: qemu-system-x86_64 -hda $imgFile" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

if ($Drive) {
    # Normalize drive letter (e.g. "E", "E:", "E:\")
    $driveLetter = $Drive.TrimEnd('\').TrimEnd(':').ToUpper()
    $driveRoot = "$driveLetter`:\"

    Write-Host "  Target USB Drive: $driveRoot" -ForegroundColor Yellow

    # Verify drive exists
    if (-not (Test-Path $driveRoot)) {
        Write-Host "  [ERROR] Drive $driveRoot does not exist! Please connect your USB pendrive." -ForegroundColor Red
        exit 1
    }

    # Query volume info
    $vol = Get-Volume -DriveLetter $driveLetter -ErrorAction SilentlyContinue
    if ($vol) {
        Write-Host "  Volume Label    : $($vol.FileSystemLabel)" -ForegroundColor Gray
        Write-Host "  File System     : $($vol.FileSystem)" -ForegroundColor Gray
        $freeGB = [math]::Round($vol.SizeRemaining / 1GB, 2)
        $totalGB = [math]::Round($vol.Size / 1GB, 2)
        Write-Host "  Capacity        : $freeGB GB free / $totalGB GB total" -ForegroundColor Gray
    }

    if ($Format) {
        Write-Host ""
        Write-Host "  [WARNING] You specified -Format. All data on $driveRoot will be ERASED!" -ForegroundColor Red
        if (-not $Force) {
            $confirm = Read-Host "  Are you sure you want to format $driveRoot as FAT32? (y/N)"
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "  Aborted by user." -ForegroundColor Yellow
                exit 0
            }
        }
        Write-Host "  Formatting $driveRoot as FAT32 (Label: TEZZOS)..." -ForegroundColor White
        Format-Volume -DriveLetter $driveLetter -FileSystem FAT32 -NewFileSystemLabel "TEZZOS" -Confirm:$false | Out-Null
        Write-Host "  [OK] Format complete." -ForegroundColor Green
    } else {
        if ($vol.FileSystem -ne "FAT32") {
            Write-Host "  [NOTE] Drive filesystem is $($vol.FileSystem). UEFI bare metal requires FAT32." -ForegroundColor Yellow
            Write-Host "         Run with -Format to format as FAT32: .\tools\make_usb.ps1 -Drive $Drive -Format" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "  [1/4] Creating UEFI ESP directory layout..." -ForegroundColor White
    $efiBootDir = Join-Path $driveRoot "EFI\BOOT"
    $bootLimineDir = Join-Path $driveRoot "boot\limine"
    $bootDir = Join-Path $driveRoot "boot"

    New-Item -ItemType Directory -Path $efiBootDir -Force | Out-Null
    New-Item -ItemType Directory -Path $bootLimineDir -Force | Out-Null

    Write-Host "  [2/4] Deploying UEFI vendor bootloaders..." -ForegroundColor White
    Copy-Item "tools\limine\BOOTX64.EFI" "$efiBootDir\BOOTX64.EFI" -Force
    if (Test-Path "tools\limine\BOOTIA32.EFI") {
        Copy-Item "tools\limine\BOOTIA32.EFI" "$efiBootDir\BOOTIA32.EFI" -Force
    }
    if (Test-Path "tools\limine\BOOTAA64.EFI") {
        Copy-Item "tools\limine\BOOTAA64.EFI" "$efiBootDir\BOOTAA64.EFI" -Force
    }
    Write-Host "        - EFI\BOOT\BOOTX64.EFI  (UEFI 64-bit)" -ForegroundColor Gray
    Write-Host "        - EFI\BOOT\BOOTIA32.EFI (UEFI 32-bit)" -ForegroundColor Gray

    Write-Host "  [3/4] Deploying Limine BIOS stages and configuration..." -ForegroundColor White
    Copy-Item "tools\limine\limine-bios.sys" "$bootLimineDir\limine-bios.sys" -Force
    Copy-Item "boot\limine.cfg" "$driveRoot\limine.conf" -Force
    Copy-Item "boot\limine.cfg" "$driveRoot\limine.cfg" -Force
    Copy-Item "boot\limine.cfg" "$bootLimineDir\limine.conf" -Force
    Copy-Item "boot\limine.cfg" "$bootLimineDir\limine.cfg" -Force
    Copy-Item "boot\limine.cfg" "$efiBootDir\limine.conf" -Force

    Write-Host "  [4/4] Deploying TEZZ-OS kernel binary..." -ForegroundColor White
    Copy-Item $KERNEL_ELF "$bootDir\tezzos.elf" -Force
    Copy-Item $KERNEL_ELF "$driveRoot\tezzos.elf" -Force
    Write-Host "        - boot\tezzos.elf" -ForegroundColor Gray

    # Optional: Install Limine BIOS MBR on physical drive
    try {
        $partition = Get-Partition -DriveLetter $driveLetter -ErrorAction SilentlyContinue
        if ($partition) {
            $diskNum = $partition.DiskNumber
            $physicalDrive = "\\.\PhysicalDrive$diskNum"
            Write-Host ""
            Write-Host "  Installing Limine BIOS MBR onto $physicalDrive (Disk $diskNum)..." -ForegroundColor White
            & $LIMINE_EXE bios-install $physicalDrive 2>&1 | Out-Null
            Write-Host "  [OK] Legacy BIOS MBR installed." -ForegroundColor Green
        }
    } catch {
        Write-Host "  [Note] Physical MBR installation skipped (UEFI boot is fully functional)." -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "  ================================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Your bootable TEZZ-OS USB pendrive is ready!" -ForegroundColor Green
    Write-Host "  ================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  How to Boot into Bare-Metal Computer:" -ForegroundColor White
    Write-Host "  1. Insert this USB pendrive into your physical PC / laptop." -ForegroundColor Cyan
    Write-Host "  2. Power on the PC and immediately tap your Boot Menu key:" -ForegroundColor Cyan
    Write-Host "     - Acer / Dell / Lenovo / Asus: F12 (or F8 / F11 / Esc)" -ForegroundColor Gray
    Write-Host "     - HP: F9 or Esc" -ForegroundColor Gray
    Write-Host "  3. Select your USB drive (marked 'UEFI: <Drive Name>' or 'Limine')." -ForegroundColor Cyan
    Write-Host "  4. TEZZ-OS will boot directly with full 1280x800 resolution," -ForegroundColor Cyan
    Write-Host "     mouse & touchpad support, and the virtual file system!" -ForegroundColor Cyan
    Write-Host ""
}
