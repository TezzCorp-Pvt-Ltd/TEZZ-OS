#!/usr/bin/env bash
# build.sh — TEZZ-OS Build System (Linux/macOS/WSL)
# Usage: ./build.sh [--iso] [--run]

set -e

TEZZC="${TEZZC:-../TezzNative/TezzNative-language/bin/tezzc-linux-x64}"
BUILD_DIR="./build"
ISO=0
RUN=0

for arg in "$@"; do
    case $arg in
        --iso) ISO=1 ;;
        --run) RUN=1 ;;
    esac
done

echo ""
echo "  ╔═══════════════════════════════╗"
echo "  ║   TEZZ-OS Build System 0.1   ║"
echo "  ╚═══════════════════════════════╝"
echo ""

mkdir -p "$BUILD_DIR"

if [ ! -f "$TEZZC" ]; then
    echo "  [ERROR] tezzc not found at: $TEZZC"
    echo "  Set TEZZC env var to your tezzc binary."
    exit 1
fi

echo "  [1/4] Compiling kernel..."
"$TEZZC" buildexe --target=x86_64-bare kernel/main.tn "$BUILD_DIR/tezzos.elf"
echo "  [1/4] OK — tezzos.elf"

if [ $ISO -eq 1 ]; then
    echo "  [2/4] Creating bootable ISO..."
    ISO_ROOT="$BUILD_DIR/iso_root"
    mkdir -p "$ISO_ROOT/boot/limine"
    cp boot/limine.cfg "$ISO_ROOT/"
    cp "$BUILD_DIR/tezzos.elf" "$ISO_ROOT/boot/"

    # Limine
    if [ ! -d "tools/limine" ]; then
        echo "  Downloading Limine..."
        mkdir -p tools/limine
        wget -q "https://github.com/limine-bootloader/limine/releases/download/v7.x-binary/limine-v7.x-binary.zip" \
             -O tools/limine.zip
        unzip -q tools/limine.zip -d tools/limine
        rm tools/limine.zip
    fi

    cp tools/limine/limine-bios.sys "$ISO_ROOT/boot/limine/"
    cp tools/limine/limine-bios-cd.bin "$ISO_ROOT/boot/limine/"
    cp tools/limine/limine-uefi-cd.bin "$ISO_ROOT/boot/limine/"

    xorriso -as mkisofs \
        -b boot/limine/limine-bios-cd.bin \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        --efi-boot boot/limine/limine-uefi-cd.bin \
        -efi-boot-part --efi-boot-image --protective-msdos-label \
        "$ISO_ROOT" -o "$BUILD_DIR/tezzos.iso" 2>/dev/null

    ./tools/limine/limine bios-install "$BUILD_DIR/tezzos.iso"
    echo "  [2/4] OK — tezzos.iso"
else
    echo "  [2/4] SKIP (use --iso to create bootable ISO)"
fi

echo "  [3/4] Build complete!"
echo ""
echo "  Output: $BUILD_DIR/tezzos.elf"
[ $ISO -eq 1 ] && echo "  ISO:    $BUILD_DIR/tezzos.iso"

if [ $RUN -eq 1 ]; then
    echo ""
    echo "  [4/4] Launching QEMU..."
    echo ""
    QEMU_ARGS="-machine q35 -cpu qemu64 -m 256M -serial stdio -vga std"
    if [ $ISO -eq 1 ] && [ -f "$BUILD_DIR/tezzos.iso" ]; then
        qemu-system-x86_64 $QEMU_ARGS -cdrom "$BUILD_DIR/tezzos.iso" -boot d
    else
        qemu-system-x86_64 $QEMU_ARGS -kernel "$BUILD_DIR/tezzos.elf"
    fi
else
    echo "  [4/4] Use --run to launch in QEMU"
fi
echo ""
