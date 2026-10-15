import subprocess, time, socket, os
from PIL import Image

iso_file = os.path.abspath("build/tezzos.iso")
screen_file = os.path.abspath("build/screen_fb.ppm")
screen_png = os.path.abspath("build/screen_fb.png")

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
    "-serial", "tcp:127.0.0.1:5555,server,nowait",
    "-display", "none",
    "-qmp", "tcp:127.0.0.1:4444,server,nowait"
]

print("Launching QEMU with interactive TCP serial...")
p = subprocess.Popen(args)
time.sleep(2)

serial_output = []

try:
    print("Connecting to serial console...")
    ser = socket.create_connection(('127.0.0.1', 5555), timeout=5)
    ser.setblocking(False)

    def read_serial(timeout=2.0):
        out = ""
        start = time.time()
        while time.time() - start < timeout:
            try:
                data = ser.recv(4096)
                if data:
                    text = data.decode('utf-8', errors='replace')
                    out += text
                    serial_output.append(text)
            except BlockingIOError:
                pass
            time.sleep(0.05)
        return out

    # Read boot output
    print("Waiting for boot...")
    boot_text = read_serial(4.0)
    print("Booted!")

    # Test individual commands with delay
    commands = [
        "help\r",
        "version\r",
        "mem\r",
        "neofetch\r",
        "proc\r",
        "uptime\r",
        "cpuid\r"
    ]

    for cmd in commands:
        print(f"Sending: {cmd.strip()}")
        # Send character by character with 30ms delay to simulate real human typing
        for char in cmd:
            ser.sendall(char.encode('utf-8'))
            time.sleep(0.03)
        res = read_serial(1.5)
        print(f"Got response ({len(res)} chars)")

    ser.close()

    # Capture screendump of final shell state
    print("Capturing screendump...")
    s = socket.create_connection(('127.0.0.1', 4444), timeout=5)
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
    print("Error during interaction:", e)

p.terminate()
try:
    p.wait(timeout=3)
except subprocess.TimeoutExpired:
    p.kill()

print("QEMU finished.")

full_log = "".join(serial_output)
with open("build/interactive_serial.log", "w", encoding="utf-8") as f:
    f.write(full_log)

print("--- Interactive Session Log (safe preview) ---")
lines = full_log.split("\n")
for l in lines:
    safe_line = l.strip().encode('ascii', errors='replace').decode('ascii')
    if safe_line:
        print("  ", safe_line)

if os.path.exists(screen_file):
    im = Image.open(screen_file)
    print(f"Captured screen: {im.size}, mode: {im.mode}")
    im.save(screen_png)
    print("Saved build/screen_fb.png successfully!")
