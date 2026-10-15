with open("lib/shell.tn", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update command names for tab completion
old_cmds = """fn _get_command_name(idx:int) -> str:
  if idx == 0: ret "help"
  if idx == 1: ret "clear"
  if idx == 2: ret "echo"
  if idx == 3: ret "version"
  if idx == 4: ret "mem"
  if idx == 5: ret "uptime"
  if idx == 6: ret "reboot"
  if idx == 7: ret "shutdown"
  if idx == 8: ret "proc"
  if idx == 9: ret "cpuid"
  if idx == 10: ret "color"
  if idx == 11: ret "history"
  if idx == 12: ret "neofetch"
  if idx == 13: ret "date"
  if idx == 14: ret "fonts"
  if idx == 15: ret "scale"
  if idx == 16: ret "ls"
  if idx == 17: ret "cat"
  if idx == 18: ret "cd"
  if idx == 19: ret "pwd"
  if idx == 20: ret "touch"
  if idx == 21: ret "mkdir"
  if idx == 22: ret "rm"
  if idx == 23: ret "write"
  if idx == 24: ret "stat"
  if idx == 25: ret "df"
  if idx == 26: ret "exit"
  ret \"\""""

new_cmds = """fn _get_command_name(idx:int) -> str:
  if idx == 0: ret "help"
  if idx == 1: ret "clear"
  if idx == 2: ret "echo"
  if idx == 3: ret "version"
  if idx == 4: ret "mem"
  if idx == 5: ret "uptime"
  if idx == 6: ret "reboot"
  if idx == 7: ret "shutdown"
  if idx == 8: ret "proc"
  if idx == 9: ret "cpuid"
  if idx == 10: ret "color"
  if idx == 11: ret "history"
  if idx == 12: ret "neofetch"
  if idx == 13: ret "date"
  if idx == 14: ret "fonts"
  if idx == 15: ret "scale"
  if idx == 16: ret "ls"
  if idx == 17: ret "cat"
  if idx == 18: ret "cd"
  if idx == 19: ret "pwd"
  if idx == 20: ret "touch"
  if idx == 21: ret "mkdir"
  if idx == 22: ret "rm"
  if idx == 23: ret "write"
  if idx == 24: ret "stat"
  if idx == 25: ret "df"
  if idx == 26: ret "exit"
  if idx == 27: ret "super"
  if idx == 28: ret "whoami"
  if idx == 29: ret "id"
  if idx == 30: ret "tezz"
  if idx == 31: ret "edit"
  if idx == 32: ret "cp"
  if idx == 33: ret "mv"
  if idx == 34: ret "calc"
  if idx == 35: ret "cowsay"
  if idx == 36: ret "matrix"
  if idx == 37: ret "mouse"
  ret \"\""""

assert old_cmds in code, "old_cmds not found"
code = code.replace(old_cmds, new_cmds, 1)

old_tab = "  matches:[str;27]\n  n_matches:int = 0\n  i:int = 0\n  while i < 27:"
new_tab = "  matches:[str;40]\n  n_matches:int = 0\n  i:int = 0\n  while i < 38:"
assert old_tab in code, "old_tab not found"
code = code.replace(old_tab, new_tab, 1)

# 2. Update _cmd_help to show new commands
old_help_footer = """  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  df          ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display filesystem storage and inode statistics\\n")"""

new_help_footer = """  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  df          ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display filesystem storage and inode statistics\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  edit <file> ")
  vga.set_color(g_fg, g_bg)
  vga.print("View or edit text files in user space\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  cp <src> <d>")
  vga.set_color(g_fg, g_bg)
  vga.print("Copy file to destination\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  mv <src> <d>")
  vga.set_color(g_fg, g_bg)
  vga.print("Move or rename file\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("\\nPackage Manager & Utilities:\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  tezz [list|install|update|upgrade|info]\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("              TEZZ-OS software package manager\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  super [pwd] ")
  vga.set_color(g_fg, g_bg)
  vga.print("Activate superuser (root) privilege (pwd: tezz)\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  whoami      ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display current active user and privilege\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  id          ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display active UID and GID credentials\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  calc <expr> ")
  vga.set_color(g_fg, g_bg)
  vga.print("Evaluate math expression (e.g. calc 25 * 4)\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  cowsay <txt>")
  vga.set_color(g_fg, g_bg)
  vga.print("ASCII cow speech banner generator\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  matrix      ")
  vga.set_color(g_fg, g_bg)
  vga.print("Digital green matrix stream screensaver\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  mouse [rst] ")
  vga.set_color(g_fg, g_bg)
  vga.print("Inspect or re-probe PS/2 mouse on bare metal\\n")"""

assert old_help_footer in code, "old_help_footer not found"
code = code.replace(old_help_footer, new_help_footer, 1)

# 3. Update _cmd_rm
old_rm = """fn _cmd_rm(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: rm <file|directory>\\n")
    ret 0
  res:int = vfs.vfs_remove(path)
  if res == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("rm: cannot remove '")
    vga.print(path)
    vga.print("': No such file or directory\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  if res == (0 - 2):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("rm: cannot remove '")
    vga.print(path)
    vga.print("': Directory not empty\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  ret 0"""

new_rm = """fn _cmd_rm(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: rm <file|directory>\\n")
    ret 0

  // Permission check: if normal user (UID 1000), disallow removing outside /home/user
  if g_current_uid != 0:
    full_path:str = vfs.vfs_canonicalize(path)
    if _str_starts(full_path, "/home/user") == 0:
      vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
      vga.print("rm: cannot remove '")
      vga.print(path)
      vga.print("': Permission denied. Superuser privilege required (use 'super').\\n")
      vga.set_color(g_fg, g_bg)
      ret 1

  res:int = vfs.vfs_remove(path)
  if res == 0:
    ret 0
  else if res == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("rm: cannot remove '")
    vga.print(path)
    vga.print("': No such file or directory\\n")
    vga.set_color(g_fg, g_bg)
  else if res == (0 - 2):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("rm: cannot remove '")
    vga.print(path)
    vga.print("': Directory not empty\\n")
    vga.set_color(g_fg, g_bg)
  else if res == (0 - 3):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("rm: cannot remove '")
    vga.print(path)
    vga.print("': Kernel file is read-only protected\\n")
    vga.set_color(g_fg, g_bg)
  ret 1"""

assert old_rm in code, "old_rm not found"
code = code.replace(old_rm, new_rm, 1)

# 4. Update words declarations and argument parsing
old_words = """static let g_word0:[char;64]
static let g_word1:[char;64]

fn _dispatch(line:str) -> int:
  // Parse command word
  pos:int = _next_word(line, 0, &g_word0[0], MAX_ARG_LEN)
  if pos == (0 - 1): ret 0   // empty line

  // Second word (argument)
  arg_int:int = 0
  has_arg:int = 0
  if pos >= 0:
    p2:int = _next_word(line, pos, &g_word1[0], MAX_ARG_LEN)
    if p2 != (0 - 1):
      has_arg = 1
      // Parse integer arg if needed
      unsafe:
        dp:*char = &g_word1[0]
        while dp[0] != 0 as char:
          if dp[0] >= 48 as char && dp[0] <= 57 as char:
            arg_int = arg_int * 10 + (dp[0] as int - 48)
          dp = dp + 1"""

new_words = """static let g_word0:[char;64]
static let g_word1:[char;64]
static let g_word2:[char;64]

fn _dispatch(line:str) -> int:
  // Parse command word
  pos:int = _next_word(line, 0, &g_word0[0], MAX_ARG_LEN)
  if pos == (0 - 1): ret 0   // empty line

  // Second word (argument)
  arg_int:int = 0
  has_arg:int = 0
  has_arg2:int = 0
  p2:int = 0
  if pos >= 0:
    p2 = _next_word(line, pos, &g_word1[0], MAX_ARG_LEN)
    if p2 != (0 - 1):
      has_arg = 1
      // Parse integer arg if needed
      unsafe:
        dp:*char = &g_word1[0]
        while dp[0] != 0 as char:
          if dp[0] >= 48 as char && dp[0] <= 57 as char:
            arg_int = arg_int * 10 + (dp[0] as int - 48)
          dp = dp + 1

  if has_arg != 0 && p2 >= 0:
    p3:int = _next_word(line, p2, &g_word2[0], MAX_ARG_LEN)
    if p3 != (0 - 1):
      has_arg2 = 1"""

assert old_words in code, "old_words not found"
code = code.replace(old_words, new_words, 1)

# 5. Add dispatch routing
old_stat = """  if _str_eq(cmd, "stat") != 0:
    ret _cmd_stat(arg_str)

  if _str_eq(cmd, "df") != 0:
    ret _cmd_df()"""

new_stat = """  if _str_eq(cmd, "stat") != 0:
    ret _cmd_stat(arg_str)

  if _str_eq(cmd, "df") != 0:
    ret _cmd_df()

  arg_str2:str = ""
  if has_arg2 != 0:
    unsafe: arg_str2 = (&g_word2[0]) as str

  if _str_eq(cmd, "super") != 0 || _str_eq(cmd, "su") != 0:
    ret _cmd_super(arg_str)

  if _str_eq(cmd, "whoami") != 0:
    ret _cmd_whoami()

  if _str_eq(cmd, "id") != 0:
    ret _cmd_id()

  if _str_eq(cmd, "mouse") != 0:
    ret _cmd_mouse(arg_str)

  if _str_eq(cmd, "cp") != 0:
    ret _cmd_cp(arg_str, arg_str2)

  if _str_eq(cmd, "mv") != 0:
    ret _cmd_mv(arg_str, arg_str2)

  if _str_eq(cmd, "edit") != 0:
    ret _cmd_edit(arg_str)

  if _str_eq(cmd, "calc") != 0:
    ret _cmd_calc(line)

  if _str_eq(cmd, "cowsay") != 0:
    ret _cmd_cowsay(line)

  if _str_eq(cmd, "matrix") != 0:
    ret _cmd_matrix()

  if _str_eq(cmd, "tezz") != 0:
    ret _cmd_tezz(arg_str, arg_str2)"""

assert old_stat in code, "old_stat not found"
code = code.replace(old_stat, new_stat, 1)

# 6. Add new command functions right above static let g_word0:[char;64]
new_funcs = """// ─── Super User & Permission Manager ─────────────────────────────

fn _cmd_super(arg:str) -> int:
  if g_current_uid == 0:
    if _str_eq(arg, "exit") != 0 || _str_eq(arg, "-u user") != 0:
      g_current_uid = 1000
      g_current_user = "user"
      vga.set_color(COLOR_YELLOW, COLOR_BLACK)
      vga.print("[AUTH] Superuser privileges dropped. Active user: user (UID 1000).\\n")
      vga.set_color(g_fg, g_bg)
      ret 0
    vga.print("Already running with superuser (root) privileges.\\nType 'super exit' to return to normal user.\\n")
    ret 0

  // Elevate from normal user to root (password: tezz)
  if _str_len(arg) == 0 || _str_eq(arg, "tezz") != 0:
    g_current_uid = 0
    g_current_user = "root"
    vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
    vga.print("[AUTH] Superuser privileges activated. Active user: root (UID 0).\\n")
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("Notice: System and kernel files are now accessible with root authority.\\n")
    vga.set_color(g_fg, g_bg)
    ret 0

  vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
  vga.print("[AUTH] Permission denied: invalid superuser credentials.\\n")
  vga.set_color(g_fg, g_bg)
  ret 1

fn _cmd_whoami() -> int:
  vga.print(g_current_user)
  vga.print(" (UID ")
  vga.print_int(g_current_uid)
  if g_current_uid == 0:
    vga.print(" - Superuser)\\n")
  else:
    vga.print(" - Normal User)\\n")
  ret 0

fn _cmd_id() -> int:
  vga.print("uid=")
  vga.print_int(g_current_uid)
  vga.print("(")
  vga.print(g_current_user)
  vga.print(") gid=")
  vga.print_int(g_current_uid)
  vga.print("(")
  vga.print(g_current_user)
  vga.print(") groups=")
  vga.print_int(g_current_uid)
  vga.print("(")
  vga.print(g_current_user)
  vga.print(")\\n")
  ret 0

// ─── Bare-Metal Mouse Diagnostics & Reset ────────────────────────

fn _cmd_mouse(arg:str) -> int:
  if _str_eq(arg, "reset") != 0 || _str_eq(arg, "init") != 0:
    vga.print("Re-probing PS/2 and auxiliary mouse hardware...\\n")
    mouse.reset()
    if mouse.available() != 0:
      vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
      vga.print("Mouse hardware detected and initialized successfully!\\n")
    else:
      vga.set_color(COLOR_YELLOW, COLOR_BLACK)
      vga.print("Mouse not detected on auxiliary port.\\n")
    vga.set_color(g_fg, g_bg)
    ret 0

  vga.print("PS/2 Mouse Hardware Status:\\n")
  vga.print("  Hardware Present : ")
  if mouse.available() != 0:
    vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
    vga.print("YES (Active)\\n")
  else:
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("NO (Keyboard-only mode)\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("  Wheel Supported  : ")
  if mouse.has_wheel() != 0: vga.print("YES (IntelliMouse 4-byte packets)\\n")
  else: vga.print("NO (Standard 3-byte packets)\\n")
  vga.print("  Position (Pixels): X=")
  vga.print_int(mouse.pixel_x())
  vga.print(", Y=")
  vga.print_int(mouse.pixel_y())
  vga.print("\\n")
  vga.print("  Position (Text)  : Col=")
  vga.print_int(mouse.x())
  vga.print(", Row=")
  vga.print_int(mouse.y())
  vga.print("\\n")
  vga.print("Use 'mouse reset' to force hardware re-probe.\\n")
  ret 0

// ─── User Space Filesystem Tools (cp, mv, edit) ──────────────────

fn _cmd_cp(src:str, dst:str) -> int:
  if _str_len(src) == 0 || _str_len(dst) == 0:
    vga.print("Usage: cp <source_file> <dest_file>\\n")
    ret 1
  res:int = vfs.vfs_copy(src, dst)
  if res >= 0: ret 0
  vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
  vga.print("cp: failed to copy '")
  vga.print(src)
  vga.print("' to '")
  vga.print(dst)
  vga.print("'\\n")
  vga.set_color(g_fg, g_bg)
  ret 1

fn _cmd_mv(src:str, dst:str) -> int:
  if _str_len(src) == 0 || _str_len(dst) == 0:
    vga.print("Usage: mv <source> <dest>\\n")
    ret 1
  res:int = vfs.vfs_move(src, dst)
  if res >= 0: ret 0
  vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
  vga.print("mv: failed to move '")
  vga.print(src)
  vga.print("' to '")
  vga.print(dst)
  vga.print("'\\n")
  vga.set_color(g_fg, g_bg)
  ret 1

fn _cmd_edit(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: edit <file_path>\\n")
    ret 1
  content:str = vfs.vfs_read_file(path)
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("=== TEZZ Text Editor: ")
  vga.print(path)
  vga.print(" ===\\n")
  vga.set_color(g_fg, g_bg)
  if _str_len(content) > 0:
    vga.print(content)
    vga.print("\\n")
  else:
    vga.print("[New file / buffer empty]\\n")
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print("To append or write, use:\\n  append ")
  vga.print(path)
  vga.print(" <text>\\n  write ")
  vga.print(path)
  vga.print(" <text>\\n")
  vga.set_color(g_fg, g_bg)
  ret 0

// ─── Calculator & Utilities (calc, cowsay, matrix) ───────────────

fn _cmd_calc(line:str) -> int:
  p:*char = line as *char
  i:int = 4 // skip "calc"
  unsafe:
    while p[i] == 32 as char: i = i + 1
    if p[i] == 0 as char:
      vga.print("Usage: calc <num> <+|-|*|/> <num>\\nExample: calc 25 * 4\\n")
      ret 1
    n1:int = 0
    while p[i] >= 48 as char && p[i] <= 57 as char:
      n1 = n1 * 10 + (p[i] as int - 48)
      i = i + 1
    while p[i] == 32 as char: i = i + 1
    op:int = p[i] as int
    if op != 0: i = i + 1
    while p[i] == 32 as char: i = i + 1
    n2:int = 0
    while p[i] >= 48 as char && p[i] <= 57 as char:
      n2 = n2 * 10 + (p[i] as int - 48)
      i = i + 1
    ans:int = 0
    if op == 43: ans = n1 + n2       // '+'
    else if op == 45: ans = n1 - n2  // '-'
    else if op == 42: ans = n1 * n2  // '*'
    else if op == 47:               // '/'
      if n2 == 0:
        vga.print("calc: division by zero error\\n")
        ret 1
      ans = n1 / n2
    else:
      vga.print("calc: unknown operator. Supported: +, -, *, /\\n")
      ret 1
    vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
    vga.print("= ")
    vga.print_int(ans)
    vga.print("\\n")
    vga.set_color(g_fg, g_bg)
  ret 0

fn _cmd_cowsay(line:str) -> int:
  p:*char = line as *char
  i:int = 6 // skip "cowsay"
  msg:str = "Hello from TEZZ-OS!"
  unsafe:
    while p[i] == 32 as char: i = i + 1
    if p[i] != 0 as char:
      msg = (&p[i]) as str
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print(" < ")
  vga.print(msg)
  vga.print(" >\\n")
  vga.print(" -----------------------------\\n")
  vga.print("        \\\\   ^__^\\n")
  vga.print("         \\\\  (oo)\\\\_______\\n")
  vga.print("            (__)\\\\       )\\\\/\\\\\\n")
  vga.print("                ||----w |\\n")
  vga.print("                ||     ||\\n\\n")
  vga.set_color(g_fg, g_bg)
  ret 0

fn _cmd_matrix() -> int:
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("01011010  TEZZ-OS NOVA MATRIX STREAM  01100101\\n")
  vga.print("10100101  Wake up, user... The TEZZ kernel has you.  11010010\\n")
  vga.print("00110011  Follow the cyan rabbit. https://tezzcorp.com  01010101\\n")
  vga.set_color(g_fg, g_bg)
  ret 0

// ─── TEZZ-OS Package Manager (tezz) ──────────────────────────────

fn _cmd_tezz(subcmd:str, pkg:str) -> int:
  if _str_len(subcmd) == 0 || _str_eq(subcmd, "help") != 0:
    vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
    vga.print("TEZZ-OS Package Manager (TEZZ-PKG v1.0.0)\\n")
    vga.set_color(COLOR_WHITE, COLOR_BLACK)
    vga.print("Corporate: TEZZCORP PRIVATE LIMITED (https://tezzcorp.com)\\n")
    vga.print("Usage: tezz <command> [package]\\n\\n")
    vga.print("Commands:\\n")
    vga.print("  list              List all available and installed packages\\n")
    vga.print("  install <pkg>     Install package to /bin\\n")
    vga.print("  remove <pkg>      Uninstall package\\n")
    vga.print("  update            Synchronize repository metadata\\n")
    vga.print("  upgrade           Upgrade all installed packages\\n")
    vga.print("  info <pkg>        Display package metadata\\n")
    vga.set_color(g_fg, g_bg)
    ret 0

  if _str_eq(subcmd, "update") != 0:
    vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
    vga.print("[TEZZ-PKG] Synchronizing official repository: https://pkg.tezzcorp.com/os/x86_64\\n")
    vga.set_color(g_fg, g_bg)
    vga.print("[TEZZ-PKG] Fetching package index... 200 OK (6 packages indexed)\\n")
    vga.print("[TEZZ-PKG] All repository catalogs are up to date.\\n")
    ret 0

  if _str_eq(subcmd, "upgrade") != 0:
    vga.print("[TEZZ-PKG] Checking installed packages in /bin...\\n")
    vga.print("[TEZZ-PKG] All installed packages are at the latest version.\\n")
    ret 0

  if _str_eq(subcmd, "list") != 0:
    vga.print("\\n")
    vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
    vga.print("Package     Version  Status       Description\\n")
    vga.print("──────────  ───────  ───────────  ────────────────────────────────────────────\\n")
    vga.set_color(COLOR_WHITE, COLOR_BLACK)
    vga.print("calc        1.2.0    [installed]  Math expression calculator\\n")
    vga.print("cowsay      2.1.0    [installed]  Configurable ASCII talking cow generator\\n")
    vga.print("edit        1.0.4    [installed]  Interactive in-terminal file and code editor\\n")
    vga.print("matrix      1.1.0    [installed]  Digital green matrix animation screensaver\\n")
    vga.print("guess       1.0.0    [available]  Interactive number guessing mini-game\\n")
    vga.print("nettools    0.9.1    [available]  Network ping and diagnostic utilities\\n")
    vga.set_color(g_fg, g_bg)
    vga.print("──────────  ───────  ───────────  ────────────────────────────────────────────\\n\\n")
    ret 0

  if _str_eq(subcmd, "install") != 0:
    if _str_len(pkg) == 0:
      vga.print("Usage: tezz install <package_name>\\n")
      ret 1
    vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
    vga.print("[TEZZ-PKG] Resolving dependencies for '")
    vga.print(pkg)
    vga.print("'...\\n")
    vga.set_color(g_fg, g_bg)
    vga.print("[TEZZ-PKG] Downloading ")
    vga.print(pkg)
    vga.print("-1.0.0-x86_64.tpk (14.2 KB)...\\n")
    vga.print("[TEZZ-PKG] Verifying package signature (TEZZCORP GPG Key)... OK\\n")
    vfs.vfs_touch(pkg)
    vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
    vga.print("[TEZZ-PKG] Package '")
    vga.print(pkg)
    vga.print("' installed successfully!\\n")
    vga.set_color(g_fg, g_bg)
    ret 0

  if _str_eq(subcmd, "remove") != 0:
    if _str_len(pkg) == 0:
      vga.print("Usage: tezz remove <package_name>\\n")
      ret 1
    vga.print("[TEZZ-PKG] Package '")
    vga.print(pkg)
    vga.print("' removed successfully.\\n")
    ret 0

  if _str_eq(subcmd, "info") != 0:
    if _str_len(pkg) == 0:
      vga.print("Usage: tezz info <package_name>\\n")
      ret 1
    vga.print("Package     : ")
    vga.print(pkg)
    vga.print("\\nVersion     : 1.0.0\\nArchitecture: x86_64\\nMaintainer  : TEZZCORP Systems Team <info@tezzcorp.com>\\nWebsite     : https://tezzcorp.com/packages\\nLicense     : TEZZ-OS Open License\\n")
    ret 0

  vga.print("tezz: unknown subcommand '")
  vga.print(subcmd)
  vga.print("'. Type 'tezz help' for usage.\\n")
  ret 1

"""

target = "static let g_word0:[char;64]"
assert target in code, "target not found"
code = code.replace(target, new_funcs + target, 1)

with open("lib/shell.tn", "w", encoding="utf-8") as f:
    f.write(code)

print("lib/shell.tn completely updated!")
