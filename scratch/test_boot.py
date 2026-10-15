import subprocess, time, socket, os
from PIL import Image

serial_file = os.path.abspath("build/serial.log")
iso_file = os.path.abspath("build/tezzos.iso")
screen_file = os.path.abspath("build/screen_fb.ppm")
screen_png = os.path.abspath("build/screen_fb.png")

if os.path.exists(serial_file):
    os.remove(serial_file)
if os.path.exists(screen_file):
    os.remove(screen_file)

qemu = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
args = [
    qemu,
    "-machine", "q35",
    "-cpu", "qemu64",
    "-m", "256M",
    "-cdrom", iso_file,
    "-boot", "d",
    "-serial", f"file:{serial_file}",
    "-display", "none",
    "-qmp", "tcp:127.0.0.1:4444,server,nowait"
]

print("Starting QEMU...")
p = subprocess.Popen(args)
time.sleep(5)

try:
    print("Connecting to QMP...")
    s = socket.create_connection(('127.0.0.1', 4444), timeout=5)
    s.recv(1024)
    s.sendall(b'{"execute":"qmp_capabilities"}\n')
    time.sleep(0.5)
    s.recv(1024)
    dump_cmd = f'{{"execute":"screendump", "arguments":{{"filename":"{screen_file.replace(chr(92), "/")}"}}}}\n'
    s.sendall(dump_cmd.encode('utf-8'))
    time.sleep(1)
    res = s.recv(1024)
    print("QMP screendump response:", res.decode('utf-8', errors='ignore').strip())
    s.close()
except Exception as e:
    print("QMP error:", e)

p.terminate()
try:
    p.wait(timeout=3)
except subprocess.TimeoutExpired:
    p.kill()

print("QEMU finished.")

if os.path.exists(serial_file):
    print("--- Serial Log Content ---")
    with open(serial_file, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read())

if os.path.exists(screen_file):
    im = Image.open(screen_file)
    print(f"Captured screen: {im.size}, mode: {im.mode}")
    im.save(screen_png)
    print("Saved build/screen_fb.png successfully!")
