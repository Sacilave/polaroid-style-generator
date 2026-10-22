# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image

SUPPORTED = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')


def compress_images(input_dir, quality=85, recursive=True):
    root = Path(input_dir)
    if not root.exists():
        print(f'目录不存在: {root}')
        return False
    files = sorted([p for p in (root.rglob('*') if recursive else root.iterdir()) if p.is_file() and p.suffix.lower() in SUPPORTED])
    if not files:
        print('未找到图片文件')
        return False
    quality = max(1, min(100, int(quality)))
    for path in files:
        try:
            with Image.open(path) as img:
                rgb = img.convert('RGB')
                ext = path.suffix.lower()
                print(f'正在压缩: {path}')
                if ext in ('.jpg', '.jpeg'):
                    rgb.save(path, 'JPEG', quality=quality, optimize=True, progressive=True)
                elif ext == '.png':
                    rgb.save(path, 'PNG', optimize=True)
                elif ext == '.webp':
                    rgb.save(path, 'WEBP', quality=quality, method=6)
                elif ext in ('.tif', '.tiff'):
                    rgb.save(path, 'TIFF', compression='tiff_lzw')
                elif ext == '.bmp':
                    rgb.save(path, 'BMP')
        except Exception as e:
            print(f'处理失败 {path}: {e}')
    print('压缩完成！')
    return True


if __name__ == '__main__':
    directory = input('请输入要压缩的目录: ').strip().strip('"')
    q = input('请输入质量 1-100，直接回车默认85: ').strip()
    compress_images(directory, int(q) if q.isdigit() else 85)
