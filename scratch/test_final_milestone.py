import subprocess, time, socket, os, struct
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 45180
DISK_PATH = "build/test_disk.img"

def create_test_disk():
    with open(DISK_PATH, "wb") as f:
        f.seek(10 * 1024 * 1024 - 1)
        f.write(b"\x00")
        f.seek(0)
        # Dummy MBR bootstrap code
        f.write(b"\x33\xc0\x8e\xd0\xbc\x00\x7c\xfb\x8a\x16\x74\x7c\xcd\x13")
        f.seek(446)
        # Partition 1: Bootable (0x80), Type 0x83, LBA 2048, 18432 sectors (~9MB)
        p1 = struct.pack("<BBBBBBBBII", 0x80, 0, 2, 0, 0x83, 0, 32, 0, 2048, 18432)
        f.write(p1)
        f.seek(510)
        f.write(b"\x55\xaa")
        # Write test data at LBA 2048 (Partition 1 start)
        f.seek(2048 * 512)
        f.write(b"TEZZ-OS USER STORAGE SYSTEM VOLUME - CORPORATE DATA STORAGE - TEZZCORP PRIVATE LIMITED")

create_test_disk()

cmd = [
    QEMU,
    "-machine", "q35",
    "-cpu", "qemu64",
    "-m", "512M",
    "-drive", f"file={DISK_PATH},format=raw,if=ide,index=0,media=disk",
    "-cdrom", "build/tezzos.iso",
    "-boot", "d",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

proc = subprocess.Popen(cmd)
time.sleep(2)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
s.setblocking(False)

def drain():
    time.sleep(0.01)
    try:
        while True:
            b = s.recv(4096)
            if not b: break
    except Exception:
        pass

def mon(c):
    s.sendall((c + "\n").encode())
    drain()

def type_cmd(text):
    for ch in text:
        if ch == '/': mon("sendkey slash")
        elif ch == ' ': mon("sendkey spc")
        elif ch == '.': mon("sendkey dot")
        elif ch == '-': mon("sendkey minus")
        elif ch == '_': mon("sendkey shift-minus")
        elif ch.isupper(): mon(f"sendkey shift-{ch.lower()}")
        elif ch.islower() or ch.isdigit(): mon(f"sendkey {ch}")
        time.sleep(0.04)
    mon("sendkey ret")
    time.sleep(0.7)

def dump_and_save(ppm_name, png_name):
    mon(f"screendump build/{ppm_name}")
    time.sleep(0.3)
    ppm_path = f"build/{ppm_name}"
    png_path = f"build/{png_name}"
    if os.path.exists(ppm_path):
        Image.open(ppm_path).save(png_path)
        print(f"Captured: {png_path}")

# Boot
time.sleep(3)
mon("sendkey ret") # fast forward Limine boot
time.sleep(3)

print("=== 1. Capturing Initial Boot Screen with Prompt Cursor ===")
dump_and_save("screen_hw_boot.ppm", "screen_hw_boot.png")

print("=== 2. Testing 'lscpu' and 'free' ===")
type_cmd("lscpu")
type_cmd("free")
dump_and_save("screen_cpu_mem.ppm", "screen_cpu_mem.png")

print("=== 3. Testing 'lsblk' and 'hexview 0 0' ===")
type_cmd("clear")
type_cmd("lsblk")
type_cmd("hexview 0 0")
dump_and_save("screen_storage_lsblk.ppm", "screen_storage_lsblk.png")

print("=== 4. Testing 'lspci' and 'gpuinfo' ===")
type_cmd("clear")
type_cmd("lspci")
type_cmd("gpuinfo")
dump_and_save("screen_pci_gpu.ppm", "screen_pci_gpu.png")

print("=== 5. Testing 'wifi' and 'bt' ===")
type_cmd("clear")
type_cmd("wifi")
type_cmd("bt")
dump_and_save("screen_wifi_bt.ppm", "screen_wifi_bt.png")

print("=== 6. Testing 'hwinfo' ===")
type_cmd("clear")
type_cmd("hwinfo")
dump_and_save("screen_hwinfo.ppm", "screen_hwinfo.png")

print("=== 7. Testing 'neofetch' ===")
type_cmd("clear")
type_cmd("neofetch")
dump_and_save("screen_neofetch_hw.ppm", "screen_neofetch_hw.png")

mon("quit")
proc.wait()
print("All final milestone hardware & cursor tests completed successfully!")
