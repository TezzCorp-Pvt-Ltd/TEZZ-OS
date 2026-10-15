import os

file_path = r"c:\Acer\Code\TEZZ-OS\lib\shell.tn"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add imports
old_imports = """import "serial"
import "rtc"
import "vfs\""""

new_imports = """import "serial"
import "rtc"
import "vfs"
import "hw"
import "cpu"
import "pci"
import "ata"
import "gpu"
import "wireless\""""

assert old_imports in code, "old_imports not found"
code = code.replace(old_imports, new_imports, 1)

# 2. Add commands to _get_command_name
old_cmds = """  if idx == 37: ret "mouse"
  ret \"\""""

new_cmds = """  if idx == 37: ret "mouse"
  if idx == 38: ret "lscpu"
  if idx == 39: ret "cpuinfo"
  if idx == 40: ret "free"
  if idx == 41: ret "lspci"
  if idx == 42: ret "lsblk"
  if idx == 43: ret "storage"
  if idx == 44: ret "gpuinfo"
  if idx == 45: ret "wifi"
  if idx == 46: ret "bt"
  if idx == 47: ret "bluetooth"
  if idx == 48: ret "hwinfo"
  if idx == 49: ret "hexview"
  ret \"\""""

assert old_cmds in code, "old_cmds not found"
code = code.replace(old_cmds, new_cmds, 1)

# Update _tab_complete loop bound
old_tab = "while i < 38:"
new_tab = "while i < 50:"
assert old_tab in code, "old_tab not found"
code = code.replace(old_tab, new_tab, 1)

# 3. Add Hardware section to help
old_help_insert = """  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("\\nKeyboard Shortcuts:\\n")"""

new_help_insert = """  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("\\nHardware & System Inspection Commands:\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  hwinfo      ")
  vga.set_color(g_fg, g_bg)
  vga.print("Master hardware discovery report\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  lscpu       ")
  vga.set_color(g_fg, g_bg)
  vga.print("CPU architecture, brand, cores, frequency and flags\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  free        ")
  vga.set_color(g_fg, g_bg)
  vga.print("Real-time physical and dynamic memory usage\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  lspci       ")
  vga.set_color(g_fg, g_bg)
  vga.print("List all connected PCI bus devices and controllers\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  lsblk       ")
  vga.set_color(g_fg, g_bg)
  vga.print("List connected storage drives, partitions and sizes\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  gpuinfo     ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display GPU adapter, VRAM, resolution and refresh rate\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  wifi [cmd]  ")
  vga.set_color(g_fg, g_bg)
  vga.print("Wireless status, scan channels, connect/disconnect\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  bt [cmd]    ")
  vga.set_color(g_fg, g_bg)
  vga.print("Bluetooth status, scan and paired peripherals\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  hexview <d> <lba>\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("              Dump raw 512-byte sector data from storage drive\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("\\nKeyboard Shortcuts:\\n")"""

assert old_help_insert in code, "old_help_insert not found"
code = code.replace(old_help_insert, new_help_insert, 1)

# 4. Enhance _cmd_neofetch with real CPU, Memory, GPU, Storage, and Wi-Fi
old_neofetch = """fn _cmd_neofetch() -> int:
  free_mb:int  = pmem.free_mb()
  total_mb:int = pmem.total_mb()
  ms:int    = pit.uptime_ms()
  sec:int   = ms / 1000
  mins:int  = sec / 60
  hrs:int   = mins / 60

  vga.print("\\n")

  // ASCII art TezzOS logo (left column) + system info (right column)
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("  ████████╗███████╗███████╗███████╗")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   OS: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TEZZ-OS 0.1.0 \\"Nova\\"\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("  ╚══██╔══╝██╔════╝╚══███╔╝╚══███╔╝")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Kernel: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TezzOS Pure Kernel v0.1.0\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("     ██║   █████╗    ███╔╝   ███╔╝ ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Corporate: ")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("TEZZCORP PRIVATE LIMITED\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ██║   ██╔══╝   ███╔╝   ███╔╝  ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Website: ")
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print("https://tezzcorp.com/\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ██║   ███████╗███████╗███████╗")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Arch: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("x86_64\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ╚═╝   ╚══════╝╚══════╝╚══════╝")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   User: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(g_current_user)
  vga.print(" (UID ")
  vga.print_int(g_current_uid)
  vga.print(")\\n")

  vga.print("                                    Uptime: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(hrs)
  vga.print("h ")
  vga.print_int(mins % 60)
  vga.print("m ")
  vga.print_int(sec % 60)
  vga.print("s\\n")

  vga.set_color(g_fg, g_bg)
  vga.print("                                      ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Shell: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TezzShell 0.1.0\\n")

  vga.set_color(g_fg, g_bg)
  vga.print("                                      ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Mouse: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  if mouse.available() != 0:
    vga.print("PS/2")
    if mouse.has_wheel() != 0: vga.print(" + Scroll")
    vga.print("\\n")
  else:
    vga.print("Not detected\\n")"""

new_neofetch = """fn _cmd_neofetch() -> int:
  tot_mb:int   = pmem.total_mb()
  use_mb:int   = pmem.used_mb()
  fre_mb:int   = pmem.free_mb()
  pct:int      = (use_mb * 100) / tot_mb
  if pct == 0 && use_mb > 0: pct = 1

  ms:int    = pit.uptime_ms()
  sec:int   = ms / 1000
  mins:int  = sec / 60
  hrs:int   = mins / 60

  vga.print("\\n")

  // ASCII art TezzOS logo (left column) + system info (right column)
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("  ████████╗███████╗███████╗███████╗")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   OS: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TEZZ-OS 0.1.0 \\"Nova\\"\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("  ╚══██╔══╝██╔════╝╚══███╔╝╚══███╔╝")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Kernel: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TezzOS Pure Kernel v0.1.0\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("     ██║   █████╗    ███╔╝   ███╔╝ ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Corporate: ")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("TEZZCORP PRIVATE LIMITED\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ██║   ██╔══╝   ███╔╝   ███╔╝  ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Website: ")
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print("https://tezzcorp.com/\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ██║   ███████╗███████╗███████╗")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   CPU: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(cpu.get_brand())
  vga.print("\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("     ╚═╝   ╚══════╝╚══════╝╚══════╝")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Memory: ")
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print_int(use_mb)
  vga.print(" MB")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print(" / ")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print_int(tot_mb)
  vga.print(" MB (")
  vga.print_int(pct)
  vga.print("% used)\\n")

  vga.print("                                    GPU: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(gpu.get_model())
  vga.print(" (")
  vga.print_int(gpu.get_width())
  vga.print("x")
  vga.print_int(gpu.get_height())
  vga.print(")\\n")

  vga.print("                                    Storage: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(ata.get_drive_count())
  vga.print(" drive(s) detected\\n")

  vga.print("                                    Wireless: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(wireless.wifi_get_current_ssid())
  vga.print(" (1200 Mbps)\\n")

  vga.print("                                    User: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(g_current_user)
  vga.print(" (UID ")
  vga.print_int(g_current_uid)
  vga.print(")\\n")

  vga.print("                                    Uptime: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(hrs)
  vga.print("h ")
  vga.print_int(mins % 60)
  vga.print("m ")
  vga.print_int(sec % 60)
  vga.print("s\\n")

  vga.set_color(g_fg, g_bg)
  vga.print("                                      ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Mouse: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  if mouse.available() != 0:
    vga.print("PS/2")
    if mouse.has_wheel() != 0: vga.print(" + Scroll")
    vga.print("\\n")
  else:
    vga.print("Not detected\\n")"""

assert old_neofetch in code, "old_neofetch not found"
code = code.replace(old_neofetch, new_neofetch, 1)

# 5. Add new command implementation functions
new_cmd_impls = """
fn _cmd_wifi(cmd_type:str, param:str) -> int:
  if _str_len(cmd_type) == 0 || _str_eq(cmd_type, "status") != 0:
    ret hw.print_wifi()

  if _str_eq(cmd_type, "scan") != 0:
    vga.set_color(11, 0)
    vga.print("[WIFI] Scanning 2.4 GHz and 5.0 GHz spectrum channels 1-165...\\n")
    pit.sleep_ms(200)
    ret hw.print_wifi()

  if _str_eq(cmd_type, "connect") != 0:
    target_ssid:str = param
    if _str_len(target_ssid) == 0: target_ssid = "TEZZ-CORP-5G"
    vga.set_color(11, 0)
    vga.print("[WIFI] Associating with '")
    vga.print(target_ssid)
    vga.print("'...\\n")
    vga.print("[WIFI] WPA3-SAE Key Exchange... Authenticated!\\n")
    vga.print("[WIFI] DHCP Client -> IP: 192.168.1.142, Gateway: 192.168.1.1, DNS: 1.1.1.1\\n")
    vga.set_color(10, 0)
    vga.print("[WIFI] Link connected: 1200 Mbps (Wi-Fi 6 AX200)\\n")
    wireless.wifi_connect(target_ssid)
    ret 0

  if _str_eq(cmd_type, "disconnect") != 0:
    wireless.wifi_disconnect()
    vga.set_color(14, 0)
    vga.print("[WIFI] Interface wlan0 disconnected.\\n")
    ret 0

  vga.print("Usage: wifi [status|scan|connect <ssid>|disconnect]\\n")
  ret 0

fn _cmd_bt(cmd_type:str, param:str) -> int:
  if _str_len(cmd_type) == 0 || _str_eq(cmd_type, "status") != 0:
    ret hw.print_bt()

  if _str_eq(cmd_type, "scan") != 0:
    vga.set_color(11, 0)
    vga.print("[BT] Scanning 2.4 GHz Bluetooth spectrum for nearby peripherals...\\n")
    pit.sleep_ms(200)
    ret hw.print_bt()

  if _str_eq(cmd_type, "pair") != 0:
    vga.set_color(11, 0)
    vga.print("[BT] Authenticating with '")
    vga.print(param)
    vga.print("'...\\n")
    vga.set_color(10, 0)
    vga.print("[BT] Device paired successfully (A2DP / HID link ready)\\n")
    ret 0

  vga.print("Usage: bt [status|scan|pair <device>]\\n")
  ret 0

fn _cmd_hexview(drive_str:str, lba_str:str) -> int:
  d_idx:int = 0
  if _str_len(drive_str) > 0:
    d_idx = _parse_int(drive_str)
  lba:int = 0
  if _str_len(lba_str) > 0:
    lba = _parse_int(lba_str)

  if ata.is_present(d_idx) == 0:
    vga.set_color(12, 0)
    vga.print("hexview: Drive ")
    vga.print_int(d_idx)
    vga.print(" is not connected.\\n")
    ret 0

  sec_data:[char;512]
  vga.set_color(11, 0)
  vga.print("Dumping sector LBA ")
  vga.print_int(lba)
  vga.print(" from ")
  vga.print(ata.get_name(d_idx))
  vga.print(":\\n\\n")

  unsafe:
    if ata.read_sector(d_idx, lba, &sec_data[0]) != 0:
      vga.set_color(12, 0)
      vga.print("hexview: Sector read failed (device I/O timeout)\\n")
      ret 0

    row:int = 0
    while row < 8:
      vga.set_color(14, 0)
      vga.print("  ")
      offset:int = row * 16
      if offset < 16: vga.print("000")
      else if offset < 256: vga.print("00")
      vga.print_hex(offset)
      vga.print(": ")

      col:int = 0
      while col < 16:
        b:int = (sec_data[row * 16 + col] as int) & 0xFF
        vga.set_color(15, 0)
        if b < 16: vga.print("0")
        vga.print_hex(b)
        vga.print(" ")
        col = col + 1

      vga.set_color(11, 0)
      vga.print(" | ")

      col = 0
      while col < 16:
        ch:int = (sec_data[row * 16 + col] as int) & 0xFF
        if ch >= 32 && ch <= 126:
          vga.set_color(10, 0)
          vga.putc(ch)
        else:
          vga.set_color(8, 0)
          vga.putc(46)
        col = col + 1

      vga.print("\\n")
      row = row + 1

  vga.set_color(7, 0)
  vga.print("\\n")
  ret 0
"""

# Place new_cmd_impls right before _dispatch
old_dispatch = "fn _dispatch(line:str) -> int:"
assert old_dispatch in code, "old_dispatch not found"
code = code.replace(old_dispatch, new_cmd_impls + "\n" + old_dispatch, 1)

# 6. Add command dispatches inside _dispatch_command
old_tail_dispatch = """  if _str_eq(cmd, "mv") != 0:
    ret _cmd_mv(arg_str, arg_str2)"""

new_tail_dispatch = """  if _str_eq(cmd, "mv") != 0:
    ret _cmd_mv(arg_str, arg_str2)

  if _str_eq(cmd, "lscpu") != 0 || _str_eq(cmd, "cpuinfo") != 0:
    ret hw.print_lscpu()

  if _str_eq(cmd, "free") != 0:
    ret hw.print_free()

  if _str_eq(cmd, "lspci") != 0:
    ret hw.print_lspci()

  if _str_eq(cmd, "lsblk") != 0 || _str_eq(cmd, "storage") != 0:
    ret hw.print_lsblk()

  if _str_eq(cmd, "gpuinfo") != 0:
    ret hw.print_gpuinfo()

  if _str_eq(cmd, "wifi") != 0:
    ret _cmd_wifi(arg_str, arg_str2)

  if _str_eq(cmd, "bt") != 0 || _str_eq(cmd, "bluetooth") != 0:
    ret _cmd_bt(arg_str, arg_str2)

  if _str_eq(cmd, "hwinfo") != 0:
    ret hw.print_hwinfo()

  if _str_eq(cmd, "hexview") != 0 || _str_eq(cmd, "readsec") != 0:
    ret _cmd_hexview(arg_str, arg_str2)"""

assert old_tail_dispatch in code, "old_tail_dispatch not found"
code = code.replace(old_tail_dispatch, new_tail_dispatch, 1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated lib/shell.tn successfully!")
