# Python script to update lib/shell.tn with:
# 1. Terminal scrolling fix (remove auto-stick to bottom)
# 2. TEZZ banner fix (clean block Z's, corporate info)
# 3. User & Permission manager (super, whoami, id, permission enforcement)
# 4. Package manager (tezz list, install, update, upgrade, remove, info)
# 5. User space tools (edit, cp, mv, find, calc, cowsay, matrix, mouse)

with open("lib/shell.tn", "r", encoding="utf-8") as f:
    code = f.read()

# 1. State: add g_current_uid and g_current_user
old_state = "static let g_output_start_row:int = 0\n\n// Current theme\nstatic let g_fg:int = 7"
new_state = """static let g_output_start_row:int = 0

// User & Permissions
static let g_current_uid:int  = 1000     // 1000 = normal user, 0 = root
static let g_current_user:str = "user"   // "user" or "root"

// Current theme
static let g_fg:int = 7"""

assert old_state in code, "old_state not found"
code = code.replace(old_state, new_state, 1)

# 2. _print_prompt: dynamic prompt based on user ($ for user, # for root)
old_prompt = """fn _print_prompt() -> int:
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("tezz:")
  cwd:str = vfs.vfs_get_cwd_path()
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print(cwd)
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("# ")
  vga.set_color(g_fg, g_bg)
  g_prompt_len = 5 + _str_len(cwd) + 2
  ret 0"""

new_prompt = """fn _print_prompt() -> int:
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("tezz:")
  cwd:str = vfs.vfs_get_cwd_path()
  vga.set_color(COLOR_YELLOW, COLOR_BLACK)
  vga.print(cwd)
  if g_current_uid == 0:
    vga.set_color(COLOR_LIGHT_RED, COLOR_BLACK)
    vga.print("# ")
  else:
    vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
    vga.print("$ ")
  vga.set_color(g_fg, g_bg)
  g_prompt_len = 5 + _str_len(cwd) + 2
  ret 0"""

assert old_prompt in code, "old_prompt not found"
code = code.replace(old_prompt, new_prompt, 1)

# 3. Fix _cmd_neofetch logo: spell TEZZ with identical Z's and add corporate info
old_neofetch = """  // ASCII art TezzOS logo (left column) + system info (right column)
  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("    ████████╗███████╗███████╗███████╗")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   OS: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TEZZ-OS 0.1.0 \\"Nova\\"\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("       ██╔══╝██╔════╝╚══███╔╝╚════██║")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Kernel: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("TezzOS Kernel v0.1.0\\n")

  vga.set_color(COLOR_LIGHT_CYAN, COLOR_BLACK)
  vga.print("       ██║   █████╗    ███╔╝      ██╔╝")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  Arch: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print("x86_64\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("       ██║   ██╔══╝   ███╔╝      ██╔╝ ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("  CPU: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print(cpuid_vendor())
  vga.print("\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("       ██║   ███████╗███████╗    ██║  ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   RAM: ")
  vga.set_color(COLOR_LIGHT_GREEN, COLOR_BLACK)
  vga.print_int(total_mb - free_mb)
  vga.print("MB / ")
  vga.print_int(total_mb)
  vga.print("MB\\n")

  vga.set_color(COLOR_CYAN, COLOR_BLACK)
  vga.print("       ╚═╝   ╚══════╝╚══════╝   ╚═╝  ")
  vga.set_color(COLOR_WHITE, COLOR_BLACK)
  vga.print("   Uptime: ")"""

new_neofetch = """  // ASCII art TezzOS logo (left column) + system info (right column)
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

  vga.print("                                    Uptime: ")"""

assert old_neofetch in code, "old_neofetch not found"
code = code.replace(old_neofetch, new_neofetch, 1)

# 4. Mouse handle: remove auto-stick to bottom on terminal click
old_mouse = """    // Check if clicked on the right-hand scrollbar first!
    if vga.handle_scrollbar_click(ev.px, ev.py) != 0:
      ret 1

    // If scrolled up into history and user clicks anywhere in the terminal, jump to bottom
    if vga.get_scroll_offset() > 0:
      vga.scroll_to_bottom()
      ret 1

    // Left click on input row: position shell cursor"""

new_mouse = """    // Check if clicked or dragging on the right-hand scrollbar first!
    if vga.handle_scrollbar_click(ev.px, ev.py) != 0:
      ret 1

    // Left click on input row: position shell cursor"""

assert old_mouse in code, "old_mouse not found"
code = code.replace(old_mouse, new_mouse, 1)

# 5. Main loop: remove auto-stick on random keypress; only jump to bottom on Enter or End
old_key = """    // If scrolled up into history and user presses any key (other than PgUp/PgDn), jump to bottom
    if vga.get_scroll_offset() > 0 && kc != KEY_PGUP && kc != KEY_PGDN:
      vga.scroll_to_bottom()

    if kc == KEY_PGUP:"""

new_key = """    if kc == KEY_PGUP:"""

assert old_key in code, "old_key not found"
code = code.replace(old_key, new_key, 1)

old_enter = """    // ── Enter ──
    if kc == KEY_ENTER:
      vga.print("\\n")"""

new_enter = """    // ── Enter ──
    if kc == KEY_ENTER:
      if vga.get_scroll_offset() > 0:
        vga.scroll_to_bottom()
      vga.print("\\n")"""

assert old_enter in code, "old_enter not found"
code = code.replace(old_enter, new_enter, 1)

old_end = """    if kc == KEY_END:
      g_cursor = g_input_len
      vga.cursor_set(vga.cursor_row(), g_prompt_len + g_cursor)
      continue"""

new_end = """    if kc == KEY_END:
      if vga.get_scroll_offset() > 0:
        vga.scroll_to_bottom()
      g_cursor = g_input_len
      vga.cursor_set(vga.cursor_row(), g_prompt_len + g_cursor)
      continue"""

assert old_end in code, "old_end not found"
code = code.replace(old_end, new_end, 1)

with open("lib/shell.tn", "w", encoding="utf-8") as f:
    f.write(code)

print("Step 1 of shell.tn updated successfully.")
