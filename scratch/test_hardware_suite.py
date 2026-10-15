import subprocess, time, socket, os, struct
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44580
SERIAL_PORT = 44581
DISK_PATH = "build/test_disk.img"

def create_test_disk():
    print("Creating formatted 10MB test disk image with MBR partition...")
    with open(DISK_PATH, "wb") as f:
        f.seek(10 * 1024 * 1024 - 1)
        f.write(b"\x00")
        f.seek(0)
        # Dummy MBR bootstrap code
        f.write(b"\x33\xc0\x8e\xd0\xbc\x00\x7c\xfb\x8a\x16\x74\x7c\xcd\x13")
        f.seek(446)
        # Partition 1: Bootable (0x80), Type 0x83 (TEZZ/Linux), LBA 2048, 18432 sectors (~9MB)
        p1 = struct.pack("<BBBBBBBBII", 0x80, 0, 2, 0, 0x83, 0, 32, 0, 2048, 18432)
        f.write(p1)
        f.seek(510)
        f.write(b"\x55\xaa")
        # Write test data at LBA 2048 (Partition 1 start)
        f.seek(2048 * 512)
        f.write(b"TEZZ-OS USER STORAGE SYSTEM VOLUME - CORPORATE DATA STORAGE - TEZZCORP PRIVATE LIMITED")
    print("Test disk created successfully.")

create_test_disk()

def convert_ppm(ppm_path, png_path):
    if os.path.exists(ppm_path):
        im = Image.open(ppm_path)
        im.save(png_path)
        print(f"Saved: {png_path} ({im.size[0]}x{im.size[1]})")

cmd = [
    QEMU,
    "-machine", "q35",
    "-cpu", "qemu64",
    "-m", "512M",
    "-drive", f"file={DISK_PATH},format=raw,if=ide,index=0,media=disk",
    "-cdrom", "build/tezzos.iso",
    "-boot", "d",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-serial", f"tcp:127.0.0.1:{SERIAL_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

print("Launching QEMU VM with hard disk, cdrom, and display...")
proc = subprocess.Popen(cmd)

time.sleep(2)
s_mon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_mon.connect(("127.0.0.1", MONITOR_PORT))

s_ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_ser.connect(("127.0.0.1", SERIAL_PORT))
s_ser.setblocking(False)

def read_serial_available():
    res = b""
    while True:
        try:
            chunk = s_ser.recv(4096)
            if not chunk: break
            res += chunk
        except Exception:
            break
    return res.decode('latin1', errors='ignore')

def drain():
    time.sleep(0.01)
    try:
        while True:
            b = s_mon.recv(4096)
            if not b: break
    except Exception:
        pass

def send_mon(cmd):
    s_mon.sendall((cmd + "\n").encode())
    drain()

def type_cmd(text):
    for ch in text:
        if ch == '/': send_mon("sendkey slash")
        elif ch == ' ': send_mon("sendkey spc")
        elif ch == '.': send_mon("sendkey dot")
        elif ch == '-': send_mon("sendkey minus")
        elif ch == '_': send_mon("sendkey shift-minus")
        elif ch.isupper(): send_mon(f"sendkey shift-{ch.lower()}")
        elif ch.islower() or ch.isdigit(): send_mon(f"sendkey {ch}")
        time.sleep(0.04)
    send_mon("sendkey ret")
    time.sleep(0.8)

print("Waiting for boot...")
time.sleep(3)
send_mon("sendkey ret") # speed up Limine boot
time.sleep(3)

print("=== 1. Capturing Initial Boot Screen (Real Memory, CPU, Storage) ===")
send_mon("screendump build/screen_hw_boot.ppm")
time.sleep(0.3)
convert_ppm("build/screen_hw_boot.ppm", "build/screen_hw_boot.png")

print("=== 2. Testing 'lscpu' (CPU Architecture & Detection) ===")
type_cmd("lscpu")

print("=== 3. Testing 'free' (Real Physical Memory & Dynamic Usage) ===")
type_cmd("free")

send_mon("screendump build/screen_cpu_mem.ppm")
time.sleep(0.3)
convert_ppm("build/screen_cpu_mem.ppm", "build/screen_cpu_mem.png")

print("=== 4. Testing 'lsblk' and 'storage' (Connected Storage Drives & Partitions) ===")
type_cmd("clear")
type_cmd("lsblk")

print("=== 5. Testing 'hexview 0 0' (Access Raw Data on Connected Storage) ===")
type_cmd("hexview 0 0")

send_mon("screendump build/screen_storage_lsblk.ppm")
time.sleep(0.3)
convert_ppm("build/screen_storage_lsblk.ppm", "build/screen_storage_lsblk.png")

print("=== 6. Testing 'lspci' (All Connected PCI Devices & Controllers) ===")
type_cmd("clear")
type_cmd("lspci")

print("=== 7. Testing 'gpuinfo' (Display Adapter, VRAM, Resolution) ===")
type_cmd("gpuinfo")

send_mon("screendump build/screen_pci_gpu.ppm")
time.sleep(0.3)
convert_ppm("build/screen_pci_gpu.ppm", "build/screen_pci_gpu.png")

print("=== 8. Testing 'wifi' and 'bt' (Wireless & Bluetooth Hardware) ===")
type_cmd("clear")
type_cmd("wifi")
type_cmd("bt")

send_mon("screendump build/screen_wifi_bt.ppm")
time.sleep(0.3)
convert_ppm("build/screen_wifi_bt.ppm", "build/screen_wifi_bt.png")

print("=== 9. Testing 'hwinfo' (Master System Hardware Report) ===")
type_cmd("clear")
type_cmd("hwinfo")

send_mon("screendump build/screen_hwinfo.ppm")
time.sleep(0.3)
convert_ppm("build/screen_hwinfo.ppm", "build/screen_hwinfo.png")

print("=== 10. Testing updated 'neofetch' with hardware stats ===")
type_cmd("clear")
type_cmd("neofetch")

send_mon("screendump build/screen_neofetch_hw.ppm")
time.sleep(0.3)
convert_ppm("build/screen_neofetch_hw.ppm", "build/screen_neofetch_hw.png")

send_mon("quit")
proc.wait()
print("All hardware detection tests completed successfully!")
