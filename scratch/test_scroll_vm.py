import subprocess, time, socket, os
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44556

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
        elif ch == '!':
            send_qmp_cmd(s, "sendkey shift-1")
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
    "-m", "256M",
    "-cdrom", "build/tezzos.iso",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

print("Launching QEMU VM (BIOS boot from CDROM)...")
proc = subprocess.Popen(cmd)
time.sleep(5)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
time.sleep(0.5)

print("1. Sending 'help' to produce output...")
type_string(s, "help")
time.sleep(0.8)

print("2. Sending 'neofetch' to produce more output and force scrolling...")
type_string(s, "neofetch")
time.sleep(0.8)

print("3. Sending 'ls'...")
type_string(s, "ls")
time.sleep(0.8)

# Capture bottom state
send_qmp_cmd(s, "screendump build/screen_bottom.ppm")
time.sleep(0.5)
convert_ppm("build/screen_bottom.ppm", "build/screen_bottom.png")

# Now test scrolling up with PageUp
print("4. Sending 'sendkey pgup' twice...")
send_qmp_cmd(s, "sendkey pgup")
time.sleep(0.3)
send_qmp_cmd(s, "sendkey pgup")
time.sleep(0.5)

# Capture scrolled state
send_qmp_cmd(s, "screendump build/screen_scrolled_pgup.ppm")
time.sleep(0.5)
convert_ppm("build/screen_scrolled_pgup.ppm", "build/screen_scrolled_pgup.png")

# Now test mouse wheel / mouse scroll
print("5. Testing mouse wheel scroll down...")
send_qmp_cmd(s, "mouse_move 0 0 -1")
time.sleep(0.3)
send_qmp_cmd(s, "mouse_move 0 0 -1")
time.sleep(0.5)

send_qmp_cmd(s, "screendump build/screen_mouse_scroll.ppm")
time.sleep(0.5)
convert_ppm("build/screen_mouse_scroll.ppm", "build/screen_mouse_scroll.png")

# Now send a character to verify auto-scroll back to bottom prompt
print("6. Sending key 'a' to test auto-scroll to bottom...")
send_qmp_cmd(s, "sendkey a")
time.sleep(0.5)

send_qmp_cmd(s, "screendump build/screen_autobottom.ppm")
time.sleep(0.5)
convert_ppm("build/screen_autobottom.ppm", "build/screen_autobottom.png")

send_qmp_cmd(s, "quit")
proc.wait()
print("VM test finished successfully!")
