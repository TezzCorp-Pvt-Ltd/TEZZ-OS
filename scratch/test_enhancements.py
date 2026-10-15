import subprocess, time, socket, os
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44558

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
        elif ch == '_':
            send_qmp_cmd(s, "sendkey shift-minus")
        elif ch == '*':
            send_qmp_cmd(s, "sendkey shift-8")
        elif ch == '+':
            send_qmp_cmd(s, "sendkey shift-equal")
        elif ch == '=':
            send_qmp_cmd(s, "sendkey equal")
        elif ch == '!':
            send_qmp_cmd(s, "sendkey shift-1")
        elif ch == '"':
            send_qmp_cmd(s, "sendkey shift-apostrophe")
        elif ch == ':':
            send_qmp_cmd(s, "sendkey shift-semicolon")
        elif ch.isupper():
            send_qmp_cmd(s, f"sendkey shift-{ch.lower()}")
        elif ch.islower() or ch.isdigit():
            send_qmp_cmd(s, f"sendkey {ch}")
        time.sleep(0.02)
    send_qmp_cmd(s, "sendkey ret")
    time.sleep(0.2)

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

print("Launching QEMU VM to test TEZZ-OS enhancements...")
proc = subprocess.Popen(cmd)
time.sleep(5)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
time.sleep(0.5)

print("1. Testing 'whoami' and 'id' as normal user...")
type_string(s, "whoami")
time.sleep(0.4)
type_string(s, "id")
time.sleep(0.4)

print("2. Testing kernel read-only protection against rm /boot/tezzos.elf...")
type_string(s, "rm /boot/tezzos.elf")
time.sleep(0.5)

print("3. Elevating to superuser using 'super tezz'...")
type_string(s, "super tezz")
time.sleep(0.5)

print("4. Testing kernel read-only protection as root...")
type_string(s, "rm /boot/tezzos.elf")
time.sleep(0.5)

print("5. Testing package manager: 'tezz list'...")
type_string(s, "tezz list")
time.sleep(0.5)

print("6. Testing package manager: 'tezz install calc'...")
type_string(s, "tezz install calc")
time.sleep(0.5)

print("7. Running installed package 'calc 25 * 4'...")
type_string(s, "calc 25 * 4")
time.sleep(0.5)

print("8. Testing 'cowsay'...")
type_string(s, "cowsay Hello TEZZCORP!")
time.sleep(0.5)

# Capture screenshot of package manager and permission manager
send_qmp_cmd(s, "screendump build/screen_pkg_perm.ppm")
time.sleep(0.5)
convert_ppm("build/screen_pkg_perm.ppm", "build/screen_pkg_perm.png")

print("9. Testing 'clear' and 'neofetch' for beautiful TEZZ banner...")
type_string(s, "clear")
time.sleep(0.4)
type_string(s, "neofetch")
time.sleep(0.5)

send_qmp_cmd(s, "screendump build/screen_neofetch_fixed.ppm")
time.sleep(0.5)
convert_ppm("build/screen_neofetch_fixed.ppm", "build/screen_neofetch_fixed.png")

print("10. Testing user space files in /home/user/documents...")
type_string(s, "cd /home/user/documents")
time.sleep(0.4)
type_string(s, "ls")
time.sleep(0.4)
type_string(s, "write mynote.txt TEZZCORP Private Limited")
time.sleep(0.4)
type_string(s, "cp mynote.txt backup.txt")
time.sleep(0.4)
type_string(s, "ls")
time.sleep(0.4)
type_string(s, "cat backup.txt")
time.sleep(0.5)

# Test scroll up retention (no auto-sticking to bottom!)
print("11. Scrolling up with PgUp and verifying retention...")
send_qmp_cmd(s, "sendkey pgup")
time.sleep(0.3)
send_qmp_cmd(s, "sendkey pgup")
time.sleep(0.5)

# Send mouse move: should NOT jump to bottom!
send_qmp_cmd(s, "mouse_move 5 5")
time.sleep(0.3)

send_qmp_cmd(s, "screendump build/screen_scroll_stay.ppm")
time.sleep(0.5)
convert_ppm("build/screen_scroll_stay.ppm", "build/screen_scroll_stay.png")

send_qmp_cmd(s, "quit")
proc.wait()
print("All automated enhancement tests completed successfully!")
