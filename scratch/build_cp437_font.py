import urllib.request
import re

url = "https://raw.githubusercontent.com/torvalds/linux/master/lib/fonts/font_8x16.c"
data = urllib.request.urlopen(url).read().decode("utf-8")

blocks = re.split(r'/\*\s*(\d+)\s+(0x[0-9a-fA-F]+)\s+(.*?)\s*\*/', data)

out_lines = []
out_lines.append("/* ═══════════════════════════════════════════════════════════════ */")
out_lines.append("/* TEZZ-OS — High-Quality IBM CP437 VGA 8x16 Console Font Table   */")
out_lines.append("/* 256 Glyphs: ASCII 0..127 + CP437 Box-Drawing/Math/Latin 128..255*/")
out_lines.append("/* ═══════════════════════════════════════════════════════════════ */")
out_lines.append("")
out_lines.append(".section .rodata")
out_lines.append(".align 16")
out_lines.append(".global g_font_8x16")
out_lines.append("g_font_8x16:")

idx = 1
char_count = 0
while idx < len(blocks) and char_count < 256:
    c_num = blocks[idx]
    c_hex = blocks[idx+1]
    body = blocks[idx+3]
    b_bytes = re.findall(r"0x[0-9a-fA-F]{2}", body)[:16]
    out_lines.append(f"    /* Glyph {c_num} ({c_hex}) */")
    out_lines.append("    .byte " + ", ".join(b_bytes))
    char_count += 1
    idx += 4

out_lines.append("")
out_lines.append(".global g_font_blank")
out_lines.append("g_font_blank:")
out_lines.append("    .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
out_lines.append("")
out_lines.append('.section .text, "ax", @progbits')
out_lines.append(".global get_font_glyph")
out_lines.append(".type get_font_glyph, @function")
out_lines.append("get_font_glyph:")
out_lines.append("    /* RCX = character code (0..255) */")
out_lines.append("    cmp $255, %rcx")
out_lines.append("    ja .Lblank")
out_lines.append("    shl $4, %rcx")
out_lines.append("    lea g_font_8x16(%rip), %rax")
out_lines.append("    add %rcx, %rax")
out_lines.append("    ret")
out_lines.append(".Lblank:")
out_lines.append("    lea g_font_blank(%rip), %rax")
out_lines.append("    ret")
out_lines.append("")

with open("boot/font.s", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")

print(f"Successfully wrote boot/font.s with {char_count} glyphs ({len(out_lines)} lines)!")
