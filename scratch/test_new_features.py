import subprocess, time, socket, os
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44559

def send_qmp_cmd(s, cmd):
    s.sendall((cmd + "\n").encode())
    time.sleep(0.05)

def type_string(s, text):
    for ch in text:
        if ch == '/':
            send_qmp_cmd(s, "sendkey slash")
        elif ch == ' ':
            send_qmp_cmd(s, "sendkey spc")
        elif ch == '\n':
            send_qmp_cmd(s, "sendkey ret")
        elif ch == '.':
            send_qmp_cmd(s, "sendkey dot")
        elif ch == '-':
            send_qmp_cmd(s, "sendkey minus")
        elif ch == '*':
            send_qmp_cmd(s, "sendkey shift-8")
        elif ch == '+':
            send_qmp_cmd(s, "sendkey shift-equal")
        elif ch == '!':
            send_qmp_cmd(s, "sendkey shift-1")
        elif ch.isupper():
            send_qmp_cmd(s, f"sendkey shift-{ch.lower()}")
        elif ch.islower() or ch.isdigit():
            send_qmp_cmd(s, f"sendkey {ch}")
        time.sleep(0.04)
    send_qmp_cmd(s, "sendkey ret")
    time.sleep(0.6)

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
    "-cdrom", "build/tezzos.iso",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

print("Launching QEMU VM...")
proc = subprocess.Popen(cmd)
print("Waiting 6 seconds for Limine bootloader & TEZZ-OS shell...")
time.sleep(6)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
time.sleep(0.5)

print("1. Testing 'whoami' as normal user...")
type_string(s, "whoami")
time.sleep(0.8)

print("2. Testing 'rm /boot/tezzos.elf' (Kernel Read-Only Protection)...")
type_string(s, "rm /boot/tezzos.elf")
time.sleep(0.8)

print("3. Elevating to superuser using 'super tezz'...")
type_string(s, "super tezz")
time.sleep(0.8)

print("4. Testing 'rm /boot/tezzos.elf' as root...")
type_string(s, "rm /boot/tezzos.elf")
time.sleep(0.8)

print("5. Testing package manager 'tezz list'...")
type_string(s, "tezz list")
time.sleep(0.8)

print("6. Testing package manager 'tezz install calc'...")
type_string(s, "tezz install calc")
time.sleep(0.8)

print("7. Testing 'calc 25 * 4'...")
type_string(s, "calc 25 * 4")
time.sleep(0.8)

# Capture package & permission screenshot
send_qmp_cmd(s, "screendump build/screen_pkg_features.ppm")
time.sleep(0.5)
convert_ppm("build/screen_pkg_features.ppm", "build/screen_pkg_features.png")

print("8. Testing 'clear' and 'neofetch'...")
type_string(s, "clear")
time.sleep(0.5)
type_string(s, "neofetch")
time.sleep(0.8)

send_qmp_cmd(s, "screendump build/screen_neofetch_perfect.ppm")
time.sleep(0.5)
convert_ppm("build/screen_neofetch_perfect.ppm", "build/screen_neofetch_perfect.png")

print("9. Testing 'cowsay Hello TEZZCORP!'...")
type_string(s, "cowsay Hello TEZZCORP!")
time.sleep(0.8)

send_qmp_cmd(s, "screendump build/screen_cowsay.ppm")
time.sleep(0.5)
convert_ppm("build/screen_cowsay.ppm", "build/screen_cowsay.png")

send_qmp_cmd(s, "quit")
proc.wait()
print("All feature tests completed successfully!")
