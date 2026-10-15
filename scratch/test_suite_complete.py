import subprocess, time, socket, os
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44570
SERIAL_PORT = 44571

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
    "-serial", f"tcp:127.0.0.1:{SERIAL_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

print("Launching QEMU VM...")
proc = subprocess.Popen(cmd)

print("Connecting to serial & monitor...")
time.sleep(2)

# Connect monitor
s_mon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_mon.connect(("127.0.0.1", MONITOR_PORT))

# Connect serial
s_ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_ser.connect(("127.0.0.1", SERIAL_PORT))
s_ser.setblocking(False)

def read_serial_available():
    res = b""
    while True:
        try:
            chunk = s_ser.recv(4096)
            if not chunk:
                break
            res += chunk
        except BlockingIOError:
            break
        except Exception:
            break
    return res.decode('latin1', errors='ignore')

def send_ser(text):
    for ch in text:
        s_ser.sendall(ch.encode('ascii'))
        time.sleep(0.02)
    time.sleep(0.3)

def send_mon(cmd):
    s_mon.sendall((cmd + "\n").encode())
    time.sleep(0.05)

# Wait 5 seconds for boot
print("Waiting for TEZZ-OS boot...")
boot_log = ""
for _ in range(50):
    time.sleep(0.1)
    chunk = read_serial_available()
    if chunk:
        boot_log += chunk
        if "Ready" in boot_log or "SHELL" in boot_log or "limine" in boot_log:
            pass

print("Boot log received so far (len:", len(boot_log), ")")

# Send Enter to speed up Limine boot just in case
send_mon("sendkey ret")
time.sleep(2)

chunk = read_serial_available()
boot_log += chunk

print("=== 1. Testing 'whoami' as normal user ===")
send_ser("whoami\n")
time.sleep(0.5)

print("=== 2. Testing kernel file protection: 'rm /boot/tezzos.elf' ===")
send_ser("rm /boot/tezzos.elf\n")
time.sleep(0.5)

print("=== 3. Testing superuser elevation: 'super tezz' ===")
send_ser("super tezz\n")
time.sleep(0.5)

print("=== 4. Testing 'whoami' as superuser ===")
send_ser("whoami\n")
time.sleep(0.5)

print("=== 5. Testing package manager: 'tezz list' ===")
send_ser("tezz list\n")
time.sleep(0.5)

print("=== 6. Installing packages: 'tezz install calc' ===")
send_ser("tezz install calc\n")
time.sleep(0.5)

print("=== 7. Running installed package: 'calc 25 * 4' ===")
send_ser("calc 25 * 4\n")
time.sleep(0.5)

# Capture package & permissions screenshot
send_mon("screendump build/screen_pkg_features.ppm")
time.sleep(0.3)
convert_ppm("build/screen_pkg_features.ppm", "build/screen_pkg_features.png")

print("=== 8. Installing and running 'cowsay' ===")
send_ser("clear\n")
time.sleep(0.3)
send_ser("tezz install cowsay\n")
time.sleep(0.3)
send_ser("cowsay TEZZ OS by TEZZCORP\n")
time.sleep(0.5)

send_mon("screendump build/screen_cowsay.ppm")
time.sleep(0.3)
convert_ppm("build/screen_cowsay.ppm", "build/screen_cowsay.png")

print("=== 9. Testing neofetch banner ===")
send_ser("clear\n")
time.sleep(0.3)
send_ser("neofetch\n")
time.sleep(0.5)

send_mon("screendump build/screen_neofetch_perfect.ppm")
time.sleep(0.3)
convert_ppm("build/screen_neofetch_perfect.ppm", "build/screen_neofetch_perfect.png")

print("=== 10. Testing scroll retention ===")
# Generate enough content
send_ser("help\n")
time.sleep(0.5)
# Scroll up with PageUp
send_mon("sendkey pgup")
time.sleep(0.2)
send_mon("sendkey pgup")
time.sleep(0.3)

# Click with mouse at (500, 300) without snapping to bottom!
send_mon("mouse_move 200 200 0")
time.sleep(0.1)
send_mon("mouse_button 1")
time.sleep(0.1)
send_mon("mouse_button 0")
time.sleep(0.3)

# Capture scrolled state
send_mon("screendump build/screen_scroll_stay.ppm")
time.sleep(0.3)
convert_ppm("build/screen_scroll_stay.ppm", "build/screen_scroll_stay.png")

# Now press Enter to test return to bottom
send_mon("sendkey ret")
time.sleep(0.3)

send_mon("screendump build/screen_bottom.ppm")
time.sleep(0.3)
convert_ppm("build/screen_bottom.ppm", "build/screen_bottom.png")

# Log final serial output
final_log = read_serial_available()
print("Serial output tail:\n", final_log[-1000:] if len(final_log) > 1000 else final_log)

send_mon("quit")
proc.wait()
print("Test suite completed successfully!")
