import subprocess, time, socket, os

QEMU = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
MONITOR_PORT = 44555

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
    time.sleep(0.15)

cmd = [
    QEMU,
    "-machine", "q35",
    "-cpu", "qemu64",
    "-m", "256M",
    "-hda", "build/tezzos.iso",
    "-monitor", f"tcp:127.0.0.1:{MONITOR_PORT},server,nowait",
    "-vga", "std",
    "-display", "none"
]

proc = subprocess.Popen(cmd)
print("Waiting for QEMU & Limine boot (5 seconds)...")
time.sleep(5)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", MONITOR_PORT))
time.sleep(0.5)

print("Sending shell commands...")
# 1. ls
type_string(s, "ls")
time.sleep(0.5)

# 2. cd /etc
type_string(s, "cd /etc")
time.sleep(0.5)

# 3. ls
type_string(s, "ls")
time.sleep(0.5)

# 4. cat os-release
type_string(s, "cat os-release")
time.sleep(0.5)

# 5. cd /home
type_string(s, "cd /home")
time.sleep(0.5)

# 6. write note.txt Hello from Pure TezzNative Bare Metal OS!
type_string(s, "write note.txt Hello from Pure TezzNative Bare Metal OS!")
time.sleep(0.5)

# 7. cat note.txt
type_string(s, "cat note.txt")
time.sleep(0.5)

# 8. stat note.txt
type_string(s, "stat note.txt")
time.sleep(0.5)

# 9. df
type_string(s, "df")
time.sleep(0.5)

# Dump screen
ppm_path = os.path.abspath("build/screen_vfs.ppm").replace("\\", "/")
send_qmp_cmd(s, f"screendump {ppm_path}")
time.sleep(1.0)

s.close()
proc.terminate()
proc.wait()
print("Test completed and screen dumped!")
