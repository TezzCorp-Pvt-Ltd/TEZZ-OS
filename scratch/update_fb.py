fb_code = '''// ═══════════════════════════════════════════════════════════════
// TEZZ-OS — Linear Framebuffer Terminal & Graphics Driver (lib/fb.tn)
// ═══════════════════════════════════════════════════════════════

import "serial"

extern fn get_font_glyph(ascii:int) -> int
extern fn fb_put_pixel_32(addr:int, color:int) -> int
extern fn fb_get_pixel_32(addr:int) -> int
extern fn fb_fill_32(addr:int, count:int, color:int) -> int
extern fn fb_copy_32(dst:int, src:int, count:int) -> int

static let g_fb_addr:int   = 0
static let g_width:int     = 0
static let g_height:int    = 0
static let g_pitch:int     = 0
static let g_bpp:int       = 0
static let g_scale:int     = 1
static let g_cols:int      = 0
static let g_rows:int      = 0
static let g_col:int       = 0
static let g_row:int       = 0
static let g_fg:int        = 15      // white
static let g_bg:int        = 0       // black / slate
static let g_inited:int    = 0

// Mouse cursor state
static let g_mouse_x:int   = 0
static let g_mouse_y:int   = 0
static let g_mouse_vis:int = 0
static let g_mouse_bg:[int;150]      // 10x15 saved background pixels

// ─── Scrollback Buffer & Graphical Scrollbar State ───────────────
let HIST_ROWS:int  = 256
let HIST_COLS:int  = 160
let HIST_TOTAL:int = 40960           // 256 * 160

static let g_hist_ch:[char;40960]
static let g_hist_attr:[char;40960]

static let g_head_row:int      = 0   // history index currently at bottom of screen
static let g_total_lines:int   = 0   // total logical lines written
static let g_scroll_offset:int = 0   // lines scrolled up from bottom (0 = live prompt)

fn vga_to_rgb(c:int) -> int:
  if c == 0:  ret 0x000F172A   // Deep navy slate
  if c == 1:  ret 0x001E40AF   // Blue
  if c == 2:  ret 0x0016A34A   // Green
  if c == 3:  ret 0x000891B2   // Cyan
  if c == 4:  ret 0x00DC2626   // Red
  if c == 5:  ret 0x009333EA   // Magenta
  if c == 6:  ret 0x00D97706   // Brown
  if c == 7:  ret 0x0094A3B8   // Light grey
  if c == 8:  ret 0x00475569   // Dark grey
  if c == 9:  ret 0x0038BDF8   // Light blue
  if c == 10: ret 0x004ADE80   // Light green
  if c == 11: ret 0x0022D3EE   // Light cyan
  if c == 12: ret 0x00F87171   // Light red
  if c == 13: ret 0x00C084FC   // Light magenta
  if c == 14: ret 0x00FBBF24   // Yellow
  if c == 15: ret 0x00F8FAFC   // Pure bright white
  ret 0x00F8FAFC

fn is_active() -> int: ret g_inited
fn cols() -> int:      ret g_cols
fn rows() -> int:      ret g_rows
fn width() -> int:     ret g_width
fn height() -> int:    ret g_height
fn cursor_row() -> int: ret g_row
fn cursor_col() -> int: ret g_col
fn scale() -> int:     ret g_scale

fn set_color(fg:int, bg:int) -> int:
  g_fg = fg
  g_bg = bg
  ret 0

fn get_fg() -> int: ret g_fg
fn get_bg() -> int: ret g_bg

fn max_scroll() -> int:
  if g_total_lines <= g_rows: ret 0
  ms:int = g_total_lines - g_rows
  if ms > (HIST_ROWS - g_rows): ms = HIST_ROWS - g_rows
  ret ms

fn get_scroll_offset() -> int: ret g_scroll_offset

fn set_scale(s:int) -> int:
  if s != 1 && s != 2: ret (0 - 1)
  g_scale = s
  g_cols  = (g_width - 16) / (8 * g_scale)
  g_rows  = g_height / (16 * g_scale)
  g_head_row      = g_rows - 1
  g_total_lines   = g_rows
  g_scroll_offset = 0
  clear()
  ret 0

fn init(addr:int, width:int, height:int, pitch:int, bpp:int) -> int:
  if addr == 0 || width <= 0 || height <= 0: ret (0 - 1)
  g_fb_addr = addr
  g_width   = width
  g_height  = height
  g_pitch   = pitch
  g_bpp     = bpp
  g_scale   = 1
  g_cols    = (width - 16) / 8
  g_rows    = height / 16
  g_col     = 0
  g_row     = 0
  g_fg      = 15
  g_bg      = 0
  g_inited  = 1
  g_mouse_vis = 0
  g_mouse_x = width / 2
  g_mouse_y = height / 2

  g_head_row      = g_rows - 1
  g_total_lines   = g_rows
  g_scroll_offset = 0

  clear()
  ret 0

fn put_pixel(x:int, y:int, color:int) -> int:
  if x < 0 || x >= g_width || y < 0 || y >= g_height: ret 0
  fb_put_pixel_32(g_fb_addr + y * g_pitch + x * 4, color)
  ret 0

// ─── Direct Glyph Rendering ──────────────────────────────────────

fn _render_glyph(col:int, row:int, ch:int, fg_idx:int, bg_idx:int) -> int:
  if g_fb_addr == 0: ret 0
  if col < 0 || col >= g_cols || row < 0 || row >= g_rows: ret 0
  px:int = col * 8 * g_scale
  py:int = row * 16 * g_scale
  fg:int = vga_to_rgb(fg_idx)
  bg:int = vga_to_rgb(bg_idx)

  glyph_addr:int = get_font_glyph(ch)
  unsafe:
    glyph:*char = glyph_addr as *char
    r:int = 0
    if g_scale == 1:
      while r < 16:
        bits:int = glyph[r] as int
        line_addr:int = g_fb_addr + (py + r) * g_pitch + px * 4
        c:int = 0
        while c < 8:
          if (bits & (128 >> c)) != 0:
            fb_put_pixel_32(line_addr + c * 4, fg)
          else:
            fb_put_pixel_32(line_addr + c * 4, bg)
          c = c + 1
        r = r + 1
    else:
      while r < 16:
        bits:int = glyph[r] as int
        line_addr0:int = g_fb_addr + (py + r * 2) * g_pitch + px * 4
        line_addr1:int = line_addr0 + g_pitch
        c:int = 0
        while c < 8:
          color:int = bg
          if (bits & (128 >> c)) != 0: color = fg
          fb_put_pixel_32(line_addr0 + (c * 2) * 4, color)
          fb_put_pixel_32(line_addr0 + (c * 2 + 1) * 4, color)
          fb_put_pixel_32(line_addr1 + (c * 2) * 4, color)
          fb_put_pixel_32(line_addr1 + (c * 2 + 1) * 4, color)
          c = c + 1
        r = r + 1
  ret 0

fn draw_char_at(col:int, row:int, ch:int, fg_idx:int, bg_idx:int) -> int:
  if col < 0 || col >= g_cols || row < 0 || row >= g_rows: ret 0

  // 1. Record in scrollback history
  hist_line:int = (g_head_row - (g_rows - 1 - row)) & 255
  hist_idx:int  = hist_line * HIST_COLS + col
  if hist_idx >= 0 && hist_idx < HIST_TOTAL:
    unsafe:
      g_hist_ch[hist_idx]   = ch as char
      g_hist_attr[hist_idx] = (((bg_idx & 0x0F) << 4) | (fg_idx & 0x0F)) as char

  // 2. If viewing live bottom, render to screen immediately
  if g_scroll_offset == 0:
    _render_glyph(col, row, ch, fg_idx, bg_idx)

  ret 0

// ─── Graphical Scrollbar ─────────────────────────────────────────

fn draw_scrollbar() -> int:
  if g_fb_addr == 0: ret 0
  sb_x:int = g_width - 16

  c_border:int = 0x001E293B     // Slate 800
  c_track:int  = 0x000B1120     // Slate 950 deep track
  c_btn_bg:int = 0x001E293B     // Button bg
  c_btn_fg:int = 0x0038BDF8     // Sky blue arrow icon
  c_thumb:int  = 0x00475569     // Slate 600 default thumb
  if g_scroll_offset > 0:
    c_thumb = 0x000284C7        // Bright sky/cyan thumb when scrolled!

  // 1. Separator line at sb_x
  y:int = 0
  while y < g_height:
    fb_put_pixel_32(g_fb_addr + y * g_pitch + sb_x * 4, c_border)
    y = y + 1

  // 2. Track background
  y = 16
  while y < g_height - 16:
    line_addr:int = g_fb_addr + y * g_pitch + (sb_x + 1) * 4
    fb_fill_32(line_addr, 15, c_track)
    y = y + 1

  // 3. Up Button (y = 0..15)
  y = 0
  while y < 16:
    line_addr:int = g_fb_addr + y * g_pitch + (sb_x + 1) * 4
    fb_fill_32(line_addr, 15, c_btn_bg)
    y = y + 1

  // Up Arrow icon (▲)
  fb_put_pixel_32(g_fb_addr + 4 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 5 * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 5 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 5 * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 6 * g_pitch + (sb_x + 6) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 6 * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 6 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 6 * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 6 * g_pitch + (sb_x + 10) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 5) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 6) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 10) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 7 * g_pitch + (sb_x + 11) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 8 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 9 * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + 10 * g_pitch + (sb_x + 8) * 4, c_btn_fg)

  // 4. Down Button (y = g_height - 16 .. g_height - 1)
  by:int = g_height - 16
  y = by
  while y < g_height:
    line_addr:int = g_fb_addr + y * g_pitch + (sb_x + 1) * 4
    fb_fill_32(line_addr, 15, c_btn_bg)
    y = y + 1

  // Down Arrow icon (▼)
  fb_put_pixel_32(g_fb_addr + (by + 5) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 6) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 7) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 5) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 6) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 10) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 8) * g_pitch + (sb_x + 11) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 9) * g_pitch + (sb_x + 6) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 9) * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 9) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 9) * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 9) * g_pitch + (sb_x + 10) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 10) * g_pitch + (sb_x + 7) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 10) * g_pitch + (sb_x + 8) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 10) * g_pitch + (sb_x + 9) * 4, c_btn_fg)
  fb_put_pixel_32(g_fb_addr + (by + 11) * g_pitch + (sb_x + 8) * 4, c_btn_fg)

  // 5. Thumb Pill
  ms:int = max_scroll()
  track_h:int = g_height - 32
  thumb_h:int = track_h
  thumb_y:int = 16

  if ms > 0:
    total_effective:int = g_rows + ms
    thumb_h = (track_h * g_rows) / total_effective
    if thumb_h < 28: thumb_h = 28
    if thumb_h > track_h - 10: thumb_h = track_h - 10
    travel:int = track_h - thumb_h
    thumb_y = 16 + ((ms - g_scroll_offset) * travel) / ms

  // Draw rounded pill thumb
  ty:int = thumb_y
  while ty < thumb_y + thumb_h:
    line_addr:int = g_fb_addr + ty * g_pitch + (sb_x + 3) * 4
    fb_fill_32(line_addr, 11, c_thumb)
    ty = ty + 1

  // 3 grip bars in center of thumb
  if thumb_h >= 24:
    mid:int = thumb_y + thumb_h / 2
    c_grip:int = 0x00CBD5E1     // Slate 300
    fb_fill_32(g_fb_addr + (mid - 3) * g_pitch + (sb_x + 5) * 4, 7, c_grip)
    fb_fill_32(g_fb_addr + mid * g_pitch + (sb_x + 5) * 4, 7, c_grip)
    fb_fill_32(g_fb_addr + (mid + 3) * g_pitch + (sb_x + 5) * 4, 7, c_grip)

  ret 0

// ─── View Redraw & Scroll Navigation ─────────────────────────────

fn redraw_view() -> int:
  if g_fb_addr == 0: ret 0
  if g_mouse_vis != 0: mouse_erase()

  r:int = 0
  while r < g_rows:
    hist_line:int = (g_head_row - g_rows + 1 - g_scroll_offset + r) & 255
    base:int = hist_line * HIST_COLS
    c:int = 0
    while c < g_cols:
      ch:int = 0
      attr:int = 0
      unsafe:
        ch = g_hist_ch[base + c] as int
        attr = g_hist_attr[base + c] as int
      if ch == 0: ch = 32
      fg:int = attr & 0x0F
      bg:int = (attr >> 4) & 0x0F
      _render_glyph(c, r, ch, fg, bg)
      c = c + 1
    r = r + 1

  draw_scrollbar()
  ret 0

fn set_scroll_offset(offset:int) -> int:
  ms:int = max_scroll()
  if offset < 0: offset = 0
  if offset > ms: offset = ms
  if offset != g_scroll_offset:
    g_scroll_offset = offset
    redraw_view()
  ret g_scroll_offset

fn scroll_view(delta:int) -> int:
  ret set_scroll_offset(g_scroll_offset + delta)

fn page_up() -> int:
  ret scroll_view(g_rows / 2)

fn page_down() -> int:
  ret scroll_view(0 - (g_rows / 2))

fn scroll_to_bottom() -> int:
  ret set_scroll_offset(0)

fn handle_scrollbar_click(mx:int, my:int) -> int:
  if mx < g_width - 16: ret 0
  ms:int = max_scroll()

  // Top Up Button
  if my < 16:
    scroll_view(3)
    ret 1

  // Bottom Down Button
  if my >= g_height - 16:
    scroll_view(0 - 3)
    ret 1

  if ms <= 0: ret 1

  // Track click
  track_h:int = g_height - 32
  thumb_h:int = (track_h * g_rows) / (g_rows + ms)
  if thumb_h < 28: thumb_h = 28
  if thumb_h > track_h - 10: thumb_h = track_h - 10
  travel:int = track_h - thumb_h
  thumb_y:int = 16 + ((ms - g_scroll_offset) * travel) / ms

  if my < thumb_y:
    scroll_view(g_rows / 2)
    ret 1
  if my > thumb_y + thumb_h:
    scroll_view(0 - (g_rows / 2))
    ret 1

  // Proportional click
  pos_in_travel:int = (my - 16) - (thumb_h / 2)
  if pos_in_travel < 0: pos_in_travel = 0
  if pos_in_travel > travel: pos_in_travel = travel
  new_offset:int = ms - (pos_in_travel * ms) / travel
  set_scroll_offset(new_offset)
  ret 1

// ─── Screen Clear & Row Manipulation ─────────────────────────────

fn clear() -> int:
  if g_fb_addr == 0: ret 0
  if g_mouse_vis != 0: mouse_erase()
  bg:int = vga_to_rgb(g_bg)
  total_pixels:int = (g_height * g_pitch) / 4
  fb_fill_32(g_fb_addr, total_pixels, bg)
  g_col = 0
  g_row = 0
  g_head_row      = g_rows - 1
  g_total_lines   = g_rows
  g_scroll_offset = 0

  r:int = 0
  while r < g_rows:
    base:int = r * HIST_COLS
    c:int = 0
    while c < HIST_COLS:
      unsafe:
        g_hist_ch[base + c]   = 32 as char
        g_hist_attr[base + c] = (((g_bg & 0x0F) << 4) | (g_fg & 0x0F)) as char
      c = c + 1
    r = r + 1

  draw_scrollbar()
  ret 0

fn clear_row(row:int) -> int:
  if g_fb_addr == 0 || row < 0 || row >= g_rows: ret 0
  bg:int = vga_to_rgb(g_bg)
  row_h:int = 16 * g_scale
  row_addr:int = g_fb_addr + (row * row_h) * g_pitch
  pixels_per_row:int = (row_h * g_pitch) / 4
  fb_fill_32(row_addr, pixels_per_row, bg)

  hist_line:int = (g_head_row - (g_rows - 1 - row)) & 255
  base:int = hist_line * HIST_COLS
  c:int = 0
  while c < HIST_COLS:
    unsafe:
      g_hist_ch[base + c]   = 32 as char
      g_hist_attr[base + c] = (((g_bg & 0x0F) << 4) | (g_fg & 0x0F)) as char
    c = c + 1
  ret 0

fn scroll() -> int:
  if g_fb_addr == 0: ret 0
  if g_mouse_vis != 0: mouse_erase()

  // Advance circular history buffer
  g_head_row    = (g_head_row + 1) & 255
  g_total_lines = g_total_lines + 1

  // Blank out new head line in history
  base:int = g_head_row * HIST_COLS
  c:int = 0
  while c < HIST_COLS:
    unsafe:
      g_hist_ch[base + c]   = 32 as char
      g_hist_attr[base + c] = (((g_bg & 0x0F) << 4) | (g_fg & 0x0F)) as char
    c = c + 1

  if g_scroll_offset == 0:
    row_h:int = 16 * g_scale
    dst:int = g_fb_addr
    src:int = g_fb_addr + row_h * g_pitch
    pixels_to_move:int = ((g_height - row_h) * g_pitch) / 4
    fb_copy_32(dst, src, pixels_to_move)

    bg:int = vga_to_rgb(g_bg)
    last_addr:int = g_fb_addr + (g_height - row_h) * g_pitch
    last_pixels:int = (row_h * g_pitch) / 4
    fb_fill_32(last_addr, last_pixels, bg)
  else:
    g_scroll_offset = g_scroll_offset + 1
    redraw_view()

  draw_scrollbar()
  g_row = g_rows - 1
  ret 0

fn cursor_set(row:int, col:int) -> int:
  if row >= 0 && row < g_rows: g_row = row
  if col >= 0 && col < g_cols: g_col = col
  ret 0

// ─── Text Output Formatting ──────────────────────────────────────

fn putc(ch:int) -> int:
  if g_fb_addr == 0: ret 0

  if ch == 10:  // \n
    g_col = 0
    g_row = g_row + 1
    if g_row >= g_rows: scroll()
    ret 0

  if ch == 13:  // \r
    g_col = 0
    ret 0

  if ch == 8:   // \b
    if g_col > 0:
      g_col = g_col - 1
      draw_char_at(g_col, g_row, 32, g_fg, g_bg)
    ret 0

  if ch == 9:   // \t
    next_tab:int = (g_col + 4) & (0 - 4)
    while g_col < next_tab && g_col < g_cols:
      draw_char_at(g_col, g_row, 32, g_fg, g_bg)
      g_col = g_col + 1
    if g_col >= g_cols:
      g_col = 0
      g_row = g_row + 1
      if g_row >= g_rows: scroll()
    ret 0

  // Unicode mappings to CP437
  if ch == 9608: ch = 219  // █
  if ch == 9617: ch = 176  // ░
  if ch == 9618: ch = 177  // ▒
  if ch == 9619: ch = 178  // ▓
  if ch == 9604: ch = 220  // ▄
  if ch == 9600: ch = 223  // ▀
  if ch == 9632: ch = 254  // ■
  if ch == 8593: ch = 24   // ↑
  if ch == 8595: ch = 25   // ↓
  if ch == 8592: ch = 27   // ←
  if ch == 8594: ch = 26   // →
  if ch == 8226: ch = 7    // •

  draw_char_at(g_col, g_row, ch, g_fg, g_bg)
  g_col = g_col + 1
  if g_col >= g_cols:
    g_col = 0
    g_row = g_row + 1
    if g_row >= g_rows: scroll()
  ret 0

fn print(s:str) -> int:
  if s == 0 || g_fb_addr == 0: ret 0
  unsafe:
    p:*char = s as *char
    i:int = 0
    while p[i] != 0 as char:
      b0:int = p[i] as int
      if b0 == 0xE2:
        b1:int = p[i + 1] as int
        b2:int = p[i + 2] as int
        if b1 == 0x95:
          if b2 == 0x94:      putc(201)  // ╔
          else if b2 == 0x90: putc(205)  // ═
          else if b2 == 0x91: putc(186)  // ║
          else if b2 == 0x97: putc(187)  // ╗
          else if b2 == 0x9A: putc(200)  // ╚
          else if b2 == 0x9D: putc(188)  // ╝
          else if b2 == 0xA0: putc(204)  // ╠
          else if b2 == 0xA3: putc(185)  // ╣
          else if b2 == 0xA6: putc(203)  // ╦
          else if b2 == 0xA9: putc(202)  // ╩
          else if b2 == 0xAC: putc(206)  // ╬
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x94:
          if b2 == 0x80:      putc(196)  // ─
          else if b2 == 0x82: putc(179)  // │
          else if b2 == 0x8C: putc(218)  // ┌
          else if b2 == 0x90: putc(191)  // ┐
          else if b2 == 0x94: putc(192)  // └
          else if b2 == 0x98: putc(217)  // ┘
          else if b2 == 0x9C: putc(195)  // ├
          else if b2 == 0xA4: putc(180)  // ┤
          else if b2 == 0xAC: putc(194)  // ┬
          else if b2 == 0xB4: putc(193)  // ┴
          else if b2 == 0xBC: putc(197)  // ┼
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x96:
          if b2 == 0x88:      putc(219)  // █
          else if b2 == 0x84: putc(220)  // ▄
          else if b2 == 0x80: putc(223)  // ▀
          else if b2 == 0x8C: putc(221)  // ▌
          else if b2 == 0x90: putc(222)  // ▐
          else if b2 == 0x91: putc(176)  // ░
          else if b2 == 0x92: putc(177)  // ▒
          else if b2 == 0x93: putc(178)  // ▓
          else if b2 == 0xA0: putc(254)  // ■
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x88:
          if b2 == 0x9A:      putc(251)  // √
          else if b2 == 0x9E: putc(236)  // ∞
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x89:
          if b2 == 0x88:      putc(247)  // ≈
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x81 && b2 == 0xBF:
          putc(252)  // ⁿ
          i = i + 3
          continue
        else if b1 == 0x86:
          if b2 == 0x91:      putc(24)   // ↑
          else if b2 == 0x93: putc(25)   // ↓
          else if b2 == 0x90: putc(27)   // ←
          else if b2 == 0x92: putc(26)   // →
          else:               putc(32)
          i = i + 3
          continue
        else if b1 == 0x80 && b2 == 0xA2:
          putc(7)   // •
          i = i + 3
          continue
      if b0 == 0xC2:
        b1_2:int = p[i + 1] as int
        if b1_2 == 0xB1:      putc(241)  // ±
        else if b1_2 == 0xB0: putc(248)  // °
        else if b1_2 == 0xB2: putc(253)  // ²
        else if b1_2 == 0xB5: putc(230)  // µ
        else:                 putc(32)
        i = i + 2
        continue
      if b0 == 0xCE:
        b1_g:int = p[i + 1] as int
        if b1_g == 0xB1:      putc(224)  // α
        else if b1_g == 0xB2: putc(225)  // β
        else if b1_g == 0x93: putc(226)  // Γ
        else if b1_g == 0xA3: putc(228)  // Σ
        else:                 putc(32)
        i = i + 2
        continue
      if b0 == 0xCF:
        b1_p:int = p[i + 1] as int
        if b1_p == 0x80:      putc(227)  // π
        else:                 putc(32)
        i = i + 2
        continue
      putc(b0)
      i = i + 1
  ret 0

fn print_int(n:int) -> int:
  if n == 0:
    putc(48)
    ret 0
  if n < 0:
    putc(45)
    n = 0 - n
  digits:[int;20]
  count:int = 0
  while n > 0:
    unsafe: digits[count] = n % 10
    n = n / 10
    count = count + 1
  while count > 0:
    count = count - 1
    unsafe: putc(48 + digits[count])
  ret 0

fn print_hex(n:int) -> int:
  putc(48)  // 0
  putc(120) // x
  hex:str = "0123456789ABCDEF"
  unsafe:
    h:*char = hex as *char
    i:int = 60
    while i >= 0:
      nib:int = (n >> i) & 15
      putc(h[nib] as int)
      i = i - 4
  ret 0

// ─── Mouse Cursor Rendering ─────────────────────────────────────

fn mouse_erase() -> int:
  if g_fb_addr == 0 || g_mouse_vis == 0: ret 0
  mx:int = g_mouse_x
  my:int = g_mouse_y
  y:int = 0
  while y < 15:
    line_addr:int = g_fb_addr + (my + y) * g_pitch + mx * 4
    x:int = 0
    while x < 10:
      unsafe: fb_put_pixel_32(line_addr + x * 4, g_mouse_bg[y * 10 + x])
      x = x + 1
    y = y + 1
  g_mouse_vis = 0
  ret 0

fn mouse_draw(mx:int, my:int) -> int:
  if g_fb_addr == 0: ret 0
  if mx < 0: mx = 0
  if mx > g_width - 12: mx = g_width - 12
  if my < 0: my = 0
  if my > g_height - 16: my = g_height - 16

  if g_mouse_vis != 0: mouse_erase()

  g_mouse_x = mx
  g_mouse_y = my

  c_black:int = 0x00000000
  c_white:int = 0x00FFFFFF

  // 1. Save background
  y:int = 0
  while y < 15:
    line_addr:int = g_fb_addr + (my + y) * g_pitch + mx * 4
    x:int = 0
    while x < 10:
      unsafe: g_mouse_bg[y * 10 + x] = fb_get_pixel_32(line_addr + x * 4)
      x = x + 1
    y = y + 1

  // 2. Draw 10x15 arrow cursor
  row:int = 0
  while row < 15:
    line_addr:int = g_fb_addr + (my + row) * g_pitch + mx * 4
    col:int = 0
    while col < 10:
      val:int = 0
      if row == 0 && col == 0: val = 1
      else if row == 1 && (col == 0 || col == 1): val = 1
      else if row == 2:
        if col == 0 || col == 2: val = 1
        else if col == 1: val = 2
      else if row == 3:
        if col == 0 || col == 3: val = 1
        else if col > 0 && col < 3: val = 2
      else if row == 4:
        if col == 0 || col == 4: val = 1
        else if col > 0 && col < 4: val = 2
      else if row == 5:
        if col == 0 || col == 5: val = 1
        else if col > 0 && col < 5: val = 2
      else if row == 6:
        if col == 0 || col == 6: val = 1
        else if col > 0 && col < 6: val = 2
      else if row == 7:
        if col == 0 || col == 7: val = 1
        else if col > 0 && col < 7: val = 2
      else if row == 8:
        if col == 0 || col >= 4: val = 1
        else if col > 0 && col < 4: val = 2
      else if row == 9:
        if col == 0 || col == 2 || col == 5: val = 1
        else if col == 1 || col == 3 || col == 4: val = 2
      else if row == 10:
        if col == 0 || col == 1 || col == 6: val = 1
        else if col == 5: val = 2
      else if row == 11:
        if col == 0 || col == 7: val = 1
        else if col == 6: val = 2
      else if row == 12:
        if col == 7: val = 1
      else if row == 13:
        if col == 7: val = 1

      if val == 1: fb_put_pixel_32(line_addr + col * 4, c_black)
      else if val == 2: fb_put_pixel_32(line_addr + col * 4, c_white)
      col = col + 1
    row = row + 1

  g_mouse_vis = 1
  ret 0
'''

with open('lib/fb.tn', 'w', encoding='utf-8') as f:
    f.write(fb_code)

print("lib/fb.tn updated successfully.")
