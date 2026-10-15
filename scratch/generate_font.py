from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype(r'C:\Windows\Fonts\lucon.ttf', 12)

out_lines = []
out_lines.append('/* ─── 8x16 Bitmap Font Table (ASCII 32..126 + Box Drawing) ─── */')
out_lines.append('.section .rodata')
out_lines.append('.align 16')
out_lines.append('.global g_font_8x16')
out_lines.append('g_font_8x16:')

for c_code in range(32, 127):
    ch = chr(c_code)
    im = Image.new('1', (8, 16), 0)
    draw = ImageDraw.Draw(im)
    draw.text((0, 1), ch, font=font, fill=1)
    bytes_list = []
    for y in range(16):
        byte = 0
        for x in range(8):
            if im.getpixel((x, y)):
                byte |= (1 << (7 - x))
        bytes_list.append(f'0x{byte:02x}')
    out_lines.append(f'    /* ASCII {c_code} ({repr(ch)}) */')
    out_lines.append('    .byte ' + ', '.join(bytes_list))

# Box drawing characters:
# 128: ╔ (top-left double)
# 129: ═ (horizontal double)
# 130: ║ (vertical double)
# 131: ╗ (top-right double)
# 132: ╚ (bottom-left double)
# 133: ╝ (bottom-right double)
# 134: ╠ (left tee double)
# 135: ╣ (right tee double)
# 136: █ (full block)

box_chars = {
    128: [0x00, 0x00, 0x00, 0x3f, 0x3f, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x00, 0x00, 0x00], # ╔
    129: [0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00], # ═
    130: [0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36], # ║
    131: [0x00, 0x00, 0x00, 0xfc, 0xfc, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x00, 0x00, 0x00], # ╗
    132: [0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x3f, 0x3f, 0x00, 0x00, 0x00, 0x00, 0x00], # ╚
    133: [0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0xfc, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00], # ╝
    134: [0x36, 0x36, 0x36, 0x3f, 0x3f, 0x30, 0x30, 0x30, 0x30, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36], # ╠
    135: [0x36, 0x36, 0x36, 0xfc, 0xfc, 0x0c, 0x0c, 0x0c, 0x0c, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36], # ╣
    136: [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff], # █
}

for idx, b_data in box_chars.items():
    bytes_list = [f'0x{b:02x}' for b in b_data]
    out_lines.append(f'    /* Special {idx} */')
    out_lines.append('    .byte ' + ', '.join(bytes_list))

out_lines.append('.global g_font_blank')
out_lines.append('g_font_blank:')
out_lines.append('    .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

out_lines.append('.section .text, "ax", @progbits')
out_lines.append('.global get_font_glyph')
out_lines.append('.type get_font_glyph, @function')
out_lines.append('get_font_glyph:')
out_lines.append('    cmp $32, %rcx')
out_lines.append('    jl 2f')
out_lines.append('    cmp $126, %rcx')
out_lines.append('    jle 1f')
out_lines.append('    cmp $128, %rcx')
out_lines.append('    jl 2f')
out_lines.append('    cmp $136, %rcx')
out_lines.append('    jg 2f')
out_lines.append('    sub $33, %rcx')
out_lines.append('    shl $4, %rcx')
out_lines.append('    lea g_font_8x16(%rip), %rax')
out_lines.append('    add %rcx, %rax')
out_lines.append('    ret')
out_lines.append('1:')
out_lines.append('    sub $32, %rcx')
out_lines.append('    shl $4, %rcx')
out_lines.append('    lea g_font_8x16(%rip), %rax')
out_lines.append('    add %rcx, %rax')
out_lines.append('    ret')
out_lines.append('2:')
out_lines.append('    lea g_font_blank(%rip), %rax')
out_lines.append('    ret')

with open('boot/font.s', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines) + '\n')

print(f'Wrote boot/font.s ({len(out_lines)} lines)')
