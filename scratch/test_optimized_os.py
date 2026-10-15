import subprocess, time, socket, os, json
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

print("Launching QEMU with interactive TCP serial and QMP monitor...")
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

    # Test commands
    commands = [
        "help\r",
        "fonts\r",
        "date\r",
        "uptime\r",
        "mem\r",
        "neofetch\r"
    ]

    for cmd in commands:
        print(f"Sending command: {cmd.strip()}")
        for char in cmd:
            ser.sendall(char.encode('utf-8'))
            time.sleep(0.02)
        res = read_serial(1.5)
        print(f"Received response ({len(res)} bytes)")

    # Wait 3 seconds and check uptime again to prove it advances!
    print("Waiting 3.5 seconds to test uptime progression...")
    time.sleep(3.5)
    print("Sending command: uptime (second check)")
    for char in "uptime\r":
        ser.sendall(char.encode('utf-8'))
        time.sleep(0.02)
    res2 = read_serial(1.5)
    print(f"Second uptime response: {res2.strip()}")

    ser.close()

    # QMP interactions: test mouse and capture screen
    print("Connecting to QMP monitor...")
    s = socket.create_connection(('127.0.0.1', 4444), timeout=5)
    s.recv(1024)
    s.sendall(b'{"execute":"qmp_capabilities"}\n')
    time.sleep(0.3)
    s.recv(1024)

    # Test mouse wheel event via QMP input-send-event
    try:
        wheel_event = {
            "execute": "input-send-event",
            "arguments": {
                "events": [
                    {"type": "rel", "data": {"axis": "wheel", "value": 1}}
                ]
            }
        }
        s.sendall((json.dumps(wheel_event) + "\n").encode('utf-8'))
        time.sleep(0.3)
        s.recv(1024)
        print("Sent QMP mouse wheel scroll event successfully!")
    except Exception as me:
        print("Mouse event note:", me)

    # Capture screendump
    print("Capturing screendump...")
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
with open("build/test_optimized.log", "w", encoding="utf-8") as f:
    f.write(full_log)

if os.path.exists(screen_file):
    im = Image.open(screen_file)
    print(f"Captured screen: {im.size}, mode: {im.mode}")
    im.save(screen_png)
    print("Saved build/screen_fb.png successfully!")
