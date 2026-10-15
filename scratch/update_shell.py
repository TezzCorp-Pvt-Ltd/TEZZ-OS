import sys

with open('lib/shell.tn', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _cmd_help to add filesystem commands
old_help_insert = """  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  scale [1|2] ")
  vga.set_color(g_fg, g_bg)
  vga.print("Set font scale: 1=compact (160x50), 2=large (80x25)\\n")"""

new_help_insert = """  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  scale [1|2] ")
  vga.set_color(g_fg, g_bg)
  vga.print("Set font scale: 1=compact (160x50), 2=large (80x25)\\n")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("\\nFilesystem Commands:\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  ls [path]   ")
  vga.set_color(g_fg, g_bg)
  vga.print("List directory contents (with permissions and sizes)\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  cd <path>   ")
  vga.set_color(g_fg, g_bg)
  vga.print("Change directory (e.g. cd /etc, cd .., cd /)\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  pwd         ")
  vga.set_color(g_fg, g_bg)
  vga.print("Print current working directory path\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  cat <file>  ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display content of text file\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  touch <file>")
  vga.set_color(g_fg, g_bg)
  vga.print("Create a new empty file\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  mkdir <dir> ")
  vga.set_color(g_fg, g_bg)
  vga.print("Create a new directory\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  rm <path>   ")
  vga.set_color(g_fg, g_bg)
  vga.print("Delete a file or empty directory\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  write <f> <t>")
  vga.set_color(g_fg, g_bg)
  vga.print("Write text into a file\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  append <f><t>")
  vga.set_color(g_fg, g_bg)
  vga.print("Append text to an existing file\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  stat <path> ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display detailed inode metadata and permissions\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  df          ")
  vga.set_color(g_fg, g_bg)
  vga.print("Display filesystem storage and inode statistics\\n")"""

assert old_help_insert in content, "old_help_insert not found"
content = content.replace(old_help_insert, new_help_insert, 1)

# 2. Add filesystem commands before _dispatch
old_dispatch_marker = """// ─── Command dispatch ────────────────────────────────────────────

static let g_word0:[char;64]
static let g_word1:[char;64]

fn _dispatch(line:str) -> int:"""

vfs_commands = """// ─── Filesystem Commands ─────────────────────────────────────────

static let g_write_buf:[char;256]

fn _cmd_pwd() -> int:
  vga.print(vfs.get_cwd_path())
  vga.print("\\n")
  ret 0

fn _cmd_cd(path:str) -> int:
  target:str = path
  if _str_len(path) == 0 || _str_eq(path, "~") != 0:
    target = "/home"
  res:int = vfs.chdir(target)
  if res != 0:
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("cd: no such directory: ")
    vga.print(target)
    vga.print("\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  ret 0

fn _cmd_ls(path:str) -> int:
  target_node:int = vfs.get_cwd_idx()
  if _str_len(path) > 0:
    resolved:int = vfs.resolve_path(path)
    if resolved == (0 - 1):
      vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
      vga.print("ls: cannot access '")
      vga.print(path)
      vga.print("': No such file or directory\\n")
      vga.set_color(g_fg, g_bg)
      ret 1
    target_node = resolved

  // If target is a file, display that single node
  if vfs.node_type(target_node) == 1:
    vga.print("-rw-r--r--  ")
    vga.print_int(vfs.node_size(target_node))
    vga.print(" B  ")
    vga.print(vfs.node_name(target_node))
    vga.print("\\n")
    ret 0

  // Display directory header
  vga.print("\\n")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("  Type   Perms      Size  Name\\n")
  vga.print("  ────  ───────  ───────  ──────────────────────\\n")

  // Always show . and ..
  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("  DIR   drwxr-xr-x     -  .\\n")
  vga.print("  DIR   drwxr-xr-x     -  ..\\n")

  child:int = vfs.node_first_child(target_node)
  count:int = 0
  total_bytes:int = 0

  while child != (0 - 1):
    ntype:int = vfs.node_type(child)
    nsize:int = vfs.node_size(child)
    nname:str = vfs.node_name(child)
    total_bytes = total_bytes + nsize
    count = count + 1

    if ntype == 2:
      vga.set_color(COLOR_LIGHT_BLUE, COLOR_BLACK)
      vga.print("  DIR   drwxr-xr-x     -  ")
      vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
      vga.print(nname)
      vga.print("/\\n")
    else:
      if ntype == 3:
        vga.set_color(COLOR_YELLOW, COLOR_BLACK)
        vga.print("  DEV   crw-rw----     0  ")
        vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
        vga.print(nname)
        vga.print("\\n")
      else:
        vga.set_color(COLOR_LIGHT_GREY, COLOR_BLACK)
        vga.print("  FILE  -rw-r--r--")
        if nsize < 10: vga.print("      ")
        else:
          if nsize < 100: vga.print("     ")
          else:
            if nsize < 1000: vga.print("    ")
            else:
              if nsize < 10000: vga.print("   ")
              else: vga.print("  ")
        vga.set_color(COLOR_WHITE, COLOR_BLACK)
        vga.print_int(nsize)
        vga.print("B  ")
        vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
        vga.print(nname)
        vga.print("\\n")

    child = vfs.node_next_sibling(child)

  vga.set_color(g_fg, g_bg)
  vga.print("  ────  ───────  ───────  ──────────────────────\\n")
  vga.print("  Total: ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print_int(count)
  vga.set_color(g_fg, g_bg)
  vga.print(" entries (")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print_int(total_bytes)
  vga.set_color(g_fg, g_bg)
  vga.print(" bytes in files)\\n\\n")
  ret 0

fn _cmd_cat(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: cat <file>\\n")
    ret 0
  node:int = vfs.resolve_path(path)
  if node == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("cat: ")
    vga.print(path)
    vga.print(": No such file or directory\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  if vfs.node_type(node) == 2:
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("cat: ")
    vga.print(path)
    vga.print(": Is a directory\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  content:str = vfs.read_file(path)
  if _str_len(content) == 0:
    ret 0
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print(content)
  vga.set_color(g_fg, g_bg)
  p:*char = content as *char
  cl:int = _str_len(content)
  unsafe:
    if cl > 0 && p[cl - 1] != 10 as char:
      vga.print("\\n")
  ret 0

fn _cmd_touch(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: touch <file>\\n")
    ret 0
  res:int = vfs.touch(path)
  if res == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("touch: cannot touch '")
    vga.print(path)
    vga.print("'\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  ret 0

fn _cmd_mkdir(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: mkdir <directory>\\n")
    ret 0
  res:int = vfs.mkdir(path)
  if res == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("mkdir: cannot create directory '")
    vga.print(path)
    vga.print("': File exists or invalid path\\n")
    vga.set_color(g_fg, g_bg)
    ret 1
  ret 0

fn _cmd_rm(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: rm <file|directory>\\n")
    ret 0
  res:int = vfs.remove(path)
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
  ret 0

fn _cmd_write(line:str, append_mode:int) -> int:
  pos:int = _next_word(line, 0, &g_word0[0], MAX_ARG_LEN)
  if pos == (0 - 1):
    vga.print("Usage: write <file> <text>\\n")
    ret 0
  p2:int = _next_word(line, pos, &g_word1[0], MAX_ARG_LEN)
  if p2 == (0 - 1):
    vga.print("Usage: write <file> <text>\\n")
    ret 0

  file_path:str = ""
  unsafe: file_path = (&g_word1[0]) as str

  p:*char = line as *char
  unsafe:
    while p[p2] == 32 as char:
      p2 = p2 + 1
    w_len:int = 0
    while p[p2] != 0 as char && w_len < 255:
      g_write_buf[w_len] = p[p2]
      w_len = w_len + 1
      p2 = p2 + 1
    g_write_buf[w_len] = 0 as char

  content:str = ""
  unsafe: content = (&g_write_buf[0]) as str

  bytes:int = 0
  if append_mode != 0:
    bytes = vfs.append_file(file_path, content)
  else:
    bytes = vfs.write_file(file_path, content)

  if bytes < 0:
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("write: failed to write to '")
    vga.print(file_path)
    vga.print("'\\n")
    vga.set_color(g_fg, g_bg)
    ret 1

  vga.print("Wrote ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(bytes)
  vga.set_color(g_fg, g_bg)
  vga.print(" bytes to '")
  vga.print(file_path)
  vga.print("'\\n")
  ret 0

fn _cmd_stat(path:str) -> int:
  if _str_len(path) == 0:
    vga.print("Usage: stat <file|directory>\\n")
    ret 0
  node:int = vfs.resolve_path(path)
  if node == (0 - 1):
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("stat: cannot stat '")
    vga.print(path)
    vga.print("': No such file or directory\\n")
    vga.set_color(g_fg, g_bg)
    ret 1

  vga.print("\\n  File: ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print(vfs.node_name(node))
  vga.print("\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("  Size: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(vfs.node_size(node))
  vga.set_color(g_fg, g_bg)
  vga.print(" bytes\\n  Type: ")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  ntype:int = vfs.node_type(node)
  if ntype == 1: vga.print("Regular File\\n")
  else:
    if ntype == 2: vga.print("Directory\\n")
    else:
      if ntype == 3: vga.print("Character Device\\n")
      else: vga.print("Unknown\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("  Node: ")
  vga.print_int(node)
  vga.print("  (Parent Node: ")
  vga.print_int(vfs.node_parent(node))
  vga.print(")\\n  Perm: 0")
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  perm:int = vfs.node_perm(node)
  vga.print_int(perm / 64)
  vga.print_int((perm / 8) % 8)
  vga.print_int(perm % 8)
  vga.set_color(g_fg, g_bg)
  vga.print("\\n\\n")
  ret 0

fn _cmd_df() -> int:
  used_nodes:int = 0
  total_bytes:int = 0
  i:int = 0
  while i < 128:
    if vfs.node_in_use(i) != 0:
      used_nodes = used_nodes + 1
      total_bytes = total_bytes + vfs.node_size(i)
    i = i + 1

  free_nodes:int = 128 - used_nodes
  node_pct:int = (used_nodes * 100) / 128

  vga.print("\\n")
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("Filesystem      Type     Inodes  Used  Free  Use%  Bytes Used  Mounted on\\n")
  vga.print("──────────  ────────  ─────────  ────  ────  ────  ──────────  ──────────\\n")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("rootfs           vfs        128    ")
  if used_nodes < 10: vga.print(" ")
  vga.print_int(used_nodes)
  vga.print("   ")
  if free_nodes < 100: vga.print(" ")
  vga.print_int(free_nodes)
  vga.print("   ")
  if node_pct < 10: vga.print(" ")
  vga.print_int(node_pct)
  vga.print("%      ")
  if total_bytes < 1000: vga.print(" ")
  vga.print_int(total_bytes)
  vga.print(" B  /\\n")
  vga.set_color(g_fg, g_bg)
  vga.print("──────────  ────────  ─────────  ────  ────  ────  ──────────  ──────────\\n\\n")
  ret 0

// ─── Command dispatch ────────────────────────────────────────────

static let g_word0:[char;64]
static let g_word1:[char;64]

fn _dispatch(line:str) -> int:"""

assert old_dispatch_marker in content, "old_dispatch_marker not found"
content = content.replace(old_dispatch_marker, vfs_commands, 1)

# 3. Add dispatch logic inside _dispatch
old_echo_dispatch = """  if _str_eq(cmd, "echo") != 0:
    // Print everything after "echo "
    p:*char = line as *char
    i:int = 4  // skip "echo"
    unsafe: if p[i] == 32 as char: i = i + 1
    unsafe:
      while p[i] != 0 as char:
        vga.putc(p[i] as int)
        i = i + 1
    vga.print("\\n")
    ret 0"""

new_echo_dispatch = """  if _str_eq(cmd, "echo") != 0:
    // Print everything after "echo "
    p:*char = line as *char
    i:int = 4  // skip "echo"
    unsafe: if p[i] == 32 as char: i = i + 1
    unsafe:
      while p[i] != 0 as char:
        vga.putc(p[i] as int)
        i = i + 1
    vga.print("\\n")
    ret 0

  arg_str:str = ""
  if has_arg != 0:
    unsafe: arg_str = (&g_word1[0]) as str

  if _str_eq(cmd, "pwd") != 0:
    ret _cmd_pwd()

  if _str_eq(cmd, "cd") != 0:
    ret _cmd_cd(arg_str)

  if _str_eq(cmd, "ls") != 0 || _str_eq(cmd, "dir") != 0:
    ret _cmd_ls(arg_str)

  if _str_eq(cmd, "cat") != 0 || _str_eq(cmd, "type") != 0:
    ret _cmd_cat(arg_str)

  if _str_eq(cmd, "touch") != 0:
    ret _cmd_touch(arg_str)

  if _str_eq(cmd, "mkdir") != 0:
    ret _cmd_mkdir(arg_str)

  if _str_eq(cmd, "rm") != 0:
    ret _cmd_rm(arg_str)

  if _str_eq(cmd, "write") != 0:
    ret _cmd_write(line, 0)

  if _str_eq(cmd, "append") != 0:
    ret _cmd_write(line, 1)

  if _str_eq(cmd, "stat") != 0:
    ret _cmd_stat(arg_str)

  if _str_eq(cmd, "df") != 0:
    ret _cmd_df()"""

assert old_echo_dispatch in content, "old_echo_dispatch not found"
content = content.replace(old_echo_dispatch, new_echo_dispatch, 1)

# 4. Replace remaining PROMPT_LEN with g_prompt_len
content = content.replace("PROMPT_LEN", "g_prompt_len")

with open('lib/shell.tn', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated lib/shell.tn")
