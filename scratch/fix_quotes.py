with open('lib/fb.tn', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("serial.log_int('SET_SCROLL_REQ', offset)", 'serial.log_int("SET_SCROLL_REQ", offset)')
text = text.replace("serial.log_int('MAX_SCROLL', ms)", 'serial.log_int("MAX_SCROLL", ms)')
text = text.replace("serial.log_int('TOTAL_LINES', g_total_lines)", 'serial.log_int("TOTAL_LINES", g_total_lines)')
text = text.replace("serial.log_int('NEW_SCROLL_OFFSET', g_scroll_offset)", 'serial.log_int("NEW_SCROLL_OFFSET", g_scroll_offset)')

with open('lib/fb.tn', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed strings in lib/fb.tn')
