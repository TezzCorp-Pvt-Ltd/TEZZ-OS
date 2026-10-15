for path in ['lib/hw.tn', 'lib/display.tn', 'lib/shell.tn']:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('import "gpu"', 'import "display"')
    c = c.replace('gpu.init()', 'display.init()')
    c = c.replace('gpu.get_vendor()', 'display.get_vendor()')
    c = c.replace('gpu.get_model()', 'display.get_model()')
    c = c.replace('gpu.get_vram_mb()', 'display.get_vram_mb()')
    c = c.replace('gpu.get_width()', 'display.get_width()')
    c = c.replace('gpu.get_height()', 'display.get_height()')
    c = c.replace('gpu.get_bpp()', 'display.get_bpp()')
    c = c.replace('gpu.get_refresh_rate()', 'display.get_refresh_rate()')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
print('Renamed gpu to display successfully!')
