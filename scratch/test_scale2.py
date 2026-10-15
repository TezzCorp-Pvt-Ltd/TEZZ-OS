import subprocess, time, socket, os
from PIL import Image

qemu = r"C:\msys64\clangarm64\bin\qemu-system-x86_64.exe"
iso_file = os.path.abspath("build/tezzos.iso")
screen_file = os.path.abspath("build/screen_scale2.ppm")
screen_png = os.path.abspath("build/screen_scale2.png")

if os.path.exists(screen_file):
    os.remove(screen_file)

args = [
    qemu, "-machine", "q35", "-cpu", "qemu64", "-m", "256M",
    "-cdrom", iso_file, "-boot", "d",
    "-serial", "tcp:127.0.0.1:5556,server,nowait",
    "-display", "none",
    "-qmp", "tcp:127.0.0.1:4445,server,nowait"
]

p = subprocess.Popen(args)
time.sleep(2)
try:
    ser = socket.create_connection(('127.0.0.1', 5556), timeout=5)
    time.sleep(3.0)  # wait for boot
    
    # send scale 2
    print("Switching to scale 2...")
    for c in "scale 2\r":
        ser.sendall(c.encode('utf-8'))
        time.sleep(0.02)
    time.sleep(1.2)
    
    # send neofetch in 2x scale
    print("Sending neofetch in scale 2...")
    for c in "neofetch\r":
        ser.sendall(c.encode('utf-8'))
        time.sleep(0.02)
    time.sleep(1.5)
    
    ser.close()
    
    # screendump
    s = socket.create_connection(('127.0.0.1', 4445), timeout=5)
    s.recv(1024)
    s.sendall(b'{"execute":"qmp_capabilities"}\n')
    time.sleep(0.3)
    s.recv(1024)
    dump_cmd = f'{{"execute":"screendump", "arguments":{{"filename":"{screen_file.replace(chr(92), "/")}"}}}}\n'
    s.sendall(dump_cmd.encode('utf-8'))
    time.sleep(0.8)
    s.recv(1024)
    s.close()
except Exception as e:
    print("Error:", e)

p.terminate()
try:
    p.wait(timeout=3)
except:
    p.kill()

if os.path.exists(screen_file):
    im = Image.open(screen_file)
    print("Scale 2 screen captured:", im.size)
    im.save(screen_png)
    print("Saved build/screen_scale2.png")
