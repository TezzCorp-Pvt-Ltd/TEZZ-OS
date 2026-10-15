import subprocess, time, socket, os
from PIL import Image

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
UEFI_BIOS = r"C:\msys64\clangarm64\share\qemu\edk2-x86_64-code.fd"
MONITOR_PORT = 44557

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
    "-pflash", UEFI_BIOS,
    "-cdrom", "build/tezzos.iso",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

print("Launching QEMU UEFI Virtual Machine with EDK2 OVMF...")
proc = subprocess.Popen(cmd)
# UEFI firmware takes a couple seconds to probe EFI boot options and launch Limine BOOTX64.EFI
time.sleep(7)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
time.sleep(0.5)

print("1. Capturing initial UEFI boot screenshot...")
send_qmp_cmd(s, "screendump build/screen_uefi_boot.ppm")
time.sleep(0.5)
convert_ppm("build/screen_uefi_boot.ppm", "build/screen_uefi_boot.png")

print("2. Sending 'neofetch' in UEFI VM...")
type_string(s, "neofetch")
time.sleep(1.0)

print("3. Sending 'stat /' in UEFI VM...")
type_string(s, "stat /")
time.sleep(1.0)

print("4. Capturing UEFI shell screenshot...")
send_qmp_cmd(s, "screendump build/screen_uefi_shell.ppm")
time.sleep(0.5)
convert_ppm("build/screen_uefi_shell.ppm", "build/screen_uefi_shell.png")

send_qmp_cmd(s, "quit")
proc.wait()
print("UEFI VM test finished successfully!")
