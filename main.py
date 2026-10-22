# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from PIL import Image

from image_enhancer import ImageEnhancer, SUPPORTED_EXTENSIONS

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = ROOT / 'images' / 'input'
DEFAULT_OUTPUT_DIR = ROOT / 'images' / 'output'
DEFAULT_CONVERTED_DIR = ROOT / 'images' / 'converted'

STYLE_EFFECTS = ImageEnhancer.get_supported_styles()['effects']
STYLE_FRAMES = ImageEnhancer.get_supported_styles()['frames']


def ensure_dirs() -> None:
    DEFAULT_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_CONVERTED_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(text: str = '') -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


def normalize_timestamp(value: str) -> Optional[str]:
    value = (value or '').strip()
    if not value:
        return ''
    if re.fullmatch(r'\d{4}\.\d{2}\.\d{2}', value):
        return value
    if re.fullmatch(r'\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}', value):
        return re.sub(r'\s+', ' ', value)
    return None


def supported_image_files(input_dir: Path, recursive: bool = False) -> List[Path]:
    if not input_dir.exists():
        return []
    iterator = input_dir.rglob('*') if recursive else input_dir.iterdir()
    return sorted([p for p in iterator if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS], key=lambda x: str(x).lower())


def style_folder_name(frame: str, effect: Optional[str]) -> str:
    return frame if not effect else f'{frame}_{effect}'


def process_image(
    input_path: Path,
    output_path: Path,
    frame_style: str,
    color_style: Optional[str] = None,
    *,
    title: str = '',
    signature: str = '',
    timestamp: str = '',
    note: str = '',
) -> bool:
    try:
        if not input_path.exists():
            safe_print(f'错误：输入文件不存在: {input_path}')
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        style_name = style_folder_name(frame_style, color_style)
        enhancer = ImageEnhancer(input_path)
        enhancer.apply_style(
            style_name,
            output_path,
            title=title if frame_style == 'polaroid' else '',
            signature=signature if frame_style == 'polaroid' else '',
            timestamp=timestamp if frame_style == 'polaroid' else '',
            note=note if frame_style == 'polaroid' else '',
        )
        safe_print(f'处理完成！框架：{frame_style}，色彩：{color_style or "原色"}，输出文件：{output_path}')
        return True
    except Exception as e:
        safe_print(f'处理过程中出现错误: {e}')
        return False


def generate_styles(
    frame_style: str,
    color_styles: Optional[Iterable[str]] = None,
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    title: str = '',
    signature: str = '',
    timestamp: str = '',
    note: str = '',
) -> bool:
    ensure_dirs()
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    files = supported_image_files(input_dir)
    if frame_style not in STYLE_FRAMES:
        safe_print(f'未知的框架样式: {frame_style}')
        return False

    effects = list(color_styles or [None])
    for effect in effects:
        if effect is not None and effect not in STYLE_EFFECTS:
            safe_print(f'未知的色彩风格: {effect}')
            return False

    if not files:
        safe_print('未找到支持格式的图片。')
        safe_print(f'请把图片放入: {input_dir}')
        safe_print('支持格式: jpg, jpeg, png, webp, bmp, tif, tiff')
        return False

    total_jobs = len(files) * len(effects)
    safe_print(f'输入目录: {input_dir}')
    safe_print(f'输出目录: {output_dir}')
    safe_print(f'找到 {len(files)} 张图片，将处理 {len(effects)} 个效果组合。')
    safe_print('输出规则：images/output/效果名称/原始文件名.原始扩展名')

    done = 0
    ok_count = 0
    fail_count = 0
    for effect in effects:
        folder = style_folder_name(frame_style, effect)
        safe_print(f'\n====== 生成效果: {folder} ======')
        for idx, input_path in enumerate(files, 1):
            done += 1
            output_path = output_dir / folder / input_path.name
            safe_print(f'\n图片 [{idx}/{len(files)}]: {input_path.name}')
            ok = process_image(
                input_path,
                output_path,
                frame_style,
                effect,
                title=title,
                signature=signature,
                timestamp=timestamp,
                note=note,
            )
            if ok:
                ok_count += 1
            else:
                fail_count += 1

    safe_print('\n====== 批量处理完成 ======')
    safe_print(f'成功: {ok_count} / {total_jobs}')
    safe_print(f'失败: {fail_count} / {total_jobs}')
    return fail_count == 0 and ok_count > 0


def generate_all_combinations(**kwargs) -> bool:
    success = True
    for frame in STYLE_FRAMES:
        success = generate_styles(frame, [None], **kwargs) and success
        for effect in STYLE_EFFECTS:
            success = generate_styles(frame, [effect], **kwargs) and success
    return success


def generate_random_combinations(count: int = 5, **kwargs) -> bool:
    combos = set()
    while len(combos) < count:
        combos.add((random.choice(STYLE_FRAMES), random.choice(STYLE_EFFECTS)))
    success = True
    for frame, effect in sorted(combos):
        success = generate_styles(frame, [effect], **kwargs) and success
    return success


def compress_directory_images(input_dir: Optional[Path] = None, quality: int = 85) -> bool:
    input_dir = Path(input_dir or input('请输入要压缩的图片目录路径: ').strip())
    quality = max(1, min(100, int(quality)))
    if not input_dir.exists():
        safe_print(f'错误：目录不存在: {input_dir}')
        return False
    files = supported_image_files(input_dir, recursive=True)
    if not files:
        safe_print(f'未找到任何图片文件: {input_dir}')
        return False
    safe_print(f'开始压缩: {input_dir}')
    safe_print(f'找到 {len(files)} 个图片文件，质量: {quality}')
    for file in files:
        try:
            with Image.open(file) as img:
                ext = file.suffix.lower()
                rgb = img.convert('RGB')
                if ext in ('.jpg', '.jpeg'):
                    rgb.save(file, 'JPEG', quality=quality, optimize=True, progressive=True)
                elif ext == '.png':
                    rgb.save(file, 'PNG', optimize=True)
                elif ext == '.webp':
                    rgb.save(file, 'WEBP', quality=quality, method=6)
                elif ext in ('.tif', '.tiff'):
                    rgb.save(file, 'TIFF', compression='tiff_lzw')
                elif ext == '.bmp':
                    rgb.save(file, 'BMP')
            safe_print(f'已压缩: {file}')
        except Exception as e:
            safe_print(f'压缩失败 {file}: {e}')
    safe_print('压缩完成！')
    return True


def check_required_dependencies() -> bool:
    safe_print('正在检测依赖项...')
    ok = True
    if sys.version_info < (3, 8):
        safe_print('Python 版本过低，建议 3.8 或更高。')
        ok = False
    for mod in ('PIL', 'numpy'):
        try:
            __import__(mod)
            safe_print(f'OK: {mod}')
        except Exception:
            safe_print(f'缺少依赖: {mod}')
            ok = False
    if not (ROOT / 'image_enhancer.py').exists():
        safe_print('缺少文件: image_enhancer.py')
        ok = False
    if not (ROOT / 'annotation_worker.py').exists():
        safe_print('缺少文件: annotation_worker.py')
        ok = False
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        safe_print(f'OK: ffmpeg -> {ffmpeg}')
    else:
        safe_print('提示：ffmpeg 未安装或未加入 PATH；只有 [4] 转换图片格式 会受影响。')
    return ok


def unique_output_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 2
    while True:
        candidate = parent / f'{stem}_{i}{suffix}'
        if not candidate.exists():
            return candidate
        i += 1


def convert_images_format(target_format: str, *, input_dir: Path = DEFAULT_INPUT_DIR, output_dir: Path = DEFAULT_CONVERTED_DIR) -> bool:
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        safe_print('错误：未找到 ffmpeg。请先安装 ffmpeg 并加入 PATH。')
        return False
    target_format = target_format.lower().lstrip('.')
    if target_format not in {'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tif', 'tiff'}:
        safe_print('不支持的目标格式。')
        return False
    files = supported_image_files(input_dir)
    if not files:
        safe_print(f'未找到可转换图片: {input_dir}')
        return False
    dest_dir = output_dir / target_format
    dest_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    for file in files:
        ext = 'jpg' if target_format == 'jpeg' else target_format
        out = unique_output_path(dest_dir / f'{file.stem}.{ext}')
        cmd = [ffmpeg, '-y', '-hide_banner', '-loglevel', 'error', '-i', str(file), str(out)]
        result = subprocess.run(cmd)
        if result.returncode == 0 and out.exists():
            success += 1
            safe_print(f'转换完成: {file.name} -> {out.name}')
        else:
            safe_print(f'转换失败: {file.name}')
    safe_print(f'格式转换完成：成功 {success}/{len(files)}')
    return success == len(files)


def ask_yes(prompt: str) -> bool:
    return input(prompt).strip().lower() in {'y', 'yes', '1', '是'}


def ask_annotation_for_polaroid():
    safe_print('\n是否为 Polaroid 底部留白添加文字信息区？')
    safe_print('说明: 只会影响 polaroid 输出; symmetric / original 会自动忽略。')
    if not ask_yes('输入 Y 添加, 直接回车跳过: '):
        return '', '', '', ''
    title = input('请输入照片标题，例如 風車の丘: ').strip()
    signature = input('请输入版权署名，直接回车默认 by zgx/Lave: ').strip() or 'by zgx/Lave'
    while True:
        ts = input('请输入时间戳, 格式 YYYY.MM.DD 或 YYYY.MM.DD HH:MM: ').strip()
        normalized = normalize_timestamp(ts)
        if normalized is not None:
            break
        safe_print('时间格式错误。示例: 2026.04.12 或 2026.04.12 18:30')
    note = input('请输入备注，例如 spring in the wind（可选, 直接回车跳过）: ').strip()
    safe_print('将添加文字信息区:')
    safe_print(f'  照片标题: {title or "无"}')
    safe_print(f'  版权署名: {signature or "无"}')
    safe_print(f'  时间戳: {normalized or "无"}')
    safe_print(f'  备注: {note or "无"}')
    return title, signature, normalized, note


def run_generation_with_confirm(runner, allow_annotation: bool = True) -> None:
    safe_print('\n当前操作会默认处理 images\\input 文件夹内全部支持图片。')
    safe_print('输出位置: images\\output\\效果名称\\原始文件名.原始扩展名')
    if not ask_yes('\n确认继续? (Y/N): '):
        safe_print('已取消。')
        return
    title = signature = timestamp = note = ''
    if allow_annotation:
        title, signature, timestamp, note = ask_annotation_for_polaroid()
    safe_print('\n开始处理...')
    try:
        ok = runner(title, signature, timestamp, note)
        safe_print('\n操作完成！' if ok else '\n操作完成，但存在失败项或未找到图片。')
    except Exception as e:
        safe_print(f'\n错误: 处理失败。原因: {e}')


def quick_menu() -> None:
    while True:
        safe_print('\n============================================')
        safe_print('         Polaroid Style Generator')
        safe_print('============================================')
        safe_print('[1] 拍立得框架 (原色)')
        safe_print('[2] 拍立得框架 + 复古效果')
        safe_print('[3] 拍立得框架 + 经典黑白')
        safe_print('[4] 拍立得框架 + 70年代风格')
        safe_print('[5] 拍立得框架的所有效果')
        safe_print('[6] 对称边框 (原色)')
        safe_print('[7] 对称边框 + 复古效果')
        safe_print('[8] 对称边框 + 经典黑白')
        safe_print('[9] 对称边框的所有效果')
        safe_print('[10] 生成5个随机组合')
        safe_print('[11] 生成所有可能的组合')
        safe_print('[12] 进入详细自由组合模式')
        safe_print('[0] 返回主菜单')
        choice = input('请输入选项数字: ').strip()
        if choice == '0':
            return
        if choice == '12':
            detailed_free_mode()
            continue
        mapping = {
            '1': lambda t, s, ts, n: generate_styles('polaroid', [None], title=t, signature=s, timestamp=ts, note=n),
            '2': lambda t, s, ts, n: generate_styles('polaroid', ['vintage'], title=t, signature=s, timestamp=ts, note=n),
            '3': lambda t, s, ts, n: generate_styles('polaroid', ['bw_classic'], title=t, signature=s, timestamp=ts, note=n),
            '4': lambda t, s, ts, n: generate_styles('polaroid', ['instant_70s'], title=t, signature=s, timestamp=ts, note=n),
            '5': lambda t, s, ts, n: generate_styles('polaroid', STYLE_EFFECTS, title=t, signature=s, timestamp=ts, note=n),
            '6': lambda t, s, ts, n: generate_styles('symmetric', [None]),
            '7': lambda t, s, ts, n: generate_styles('symmetric', ['vintage']),
            '8': lambda t, s, ts, n: generate_styles('symmetric', ['bw_classic']),
            '9': lambda t, s, ts, n: generate_styles('symmetric', STYLE_EFFECTS),
            '10': lambda t, s, ts, n: generate_random_combinations(5, title=t, signature=s, timestamp=ts, note=n),
            '11': lambda t, s, ts, n: generate_all_combinations(title=t, signature=s, timestamp=ts, note=n),
        }
        if choice not in mapping:
            safe_print('无效选项。')
            continue
        run_generation_with_confirm(mapping[choice], allow_annotation=True)
        input('按回车继续...')


def detailed_free_mode() -> None:
    safe_print('\n框架编号: [1] polaroid  [2] symmetric  [3] original')
    safe_print('色彩编号: [0] 原色  [1] vintage  [2] bw_classic  [3] instant_70s  [4] cinematic_kodak')
    raw = input('请输入组合，例如 1 0 或 1 1: ').strip().split()
    frame_map = {'1': 'polaroid', '2': 'symmetric', '3': 'original'}
    effect_map = {'0': None, '1': 'vintage', '2': 'bw_classic', '3': 'instant_70s', '4': 'cinematic_kodak'}
    if not raw or raw[0] not in frame_map:
        safe_print('框架编号无效。')
        return
    effect = None
    if len(raw) >= 2:
        if raw[1] not in effect_map:
            safe_print('色彩编号无效。')
            return
        effect = effect_map[raw[1]]
    frame = frame_map[raw[0]]
    run_generation_with_confirm(lambda t, s, ts, n: generate_styles(frame, [effect], title=t, signature=s, timestamp=ts, note=n), allow_annotation=True)


def compression_menu() -> None:
    safe_print('\n[1] 压缩 images/output')
    safe_print('[2] 手动输入目录')
    choice = input('请选择: ').strip()
    target = DEFAULT_OUTPUT_DIR if choice == '1' else Path(input('请输入目录路径: ').strip().strip('"'))
    q = input('请输入压缩质量 1-100，直接回车默认 85: ').strip()
    quality = int(q) if q.isdigit() else 85
    compress_directory_images(target, quality)


def convert_menu() -> None:
    safe_print('\n转换图片格式。输入目录: images/input')
    safe_print('[1] JPG')
    safe_print('[2] PNG')
    safe_print('[3] WEBP')
    safe_print('[4] BMP')
    safe_print('[5] TIFF')
    mapping = {'1': 'jpg', '2': 'png', '3': 'webp', '4': 'bmp', '5': 'tiff'}
    choice = input('请选择目标格式: ').strip()
    if choice not in mapping:
        safe_print('无效选项。')
        return
    convert_images_format(mapping[choice])


def interactive_menu() -> None:
    ensure_dirs()
    check_required_dependencies()
    while True:
        safe_print('\n============================================')
        safe_print('         Polaroid Style Generator')
        safe_print('============================================')
        safe_print('请选择操作方式:')
        safe_print('[1] 快捷菜单')
        safe_print('[2] 进入详细自由组合模式')
        safe_print('[3] 压缩图片')
        safe_print('[4] 转换图片格式')
        safe_print('[0] 退出')
        choice = input('请输入选项数字: ').strip()
        if choice == '1':
            quick_menu()
        elif choice == '2':
            detailed_free_mode()
        elif choice == '3':
            compression_menu()
        elif choice == '4':
            convert_menu()
        elif choice == '0':
            return
        else:
            safe_print('无效选项。')


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='图片风格处理工具')
    parser.add_argument('--interactive', action='store_true', help='进入交互菜单')
    parser.add_argument('--frame', '-f', default='polaroid', choices=STYLE_FRAMES, help='框架样式')
    parser.add_argument('--effects', '-e', nargs='*', help='色彩效果，可以指定多个')
    parser.add_argument('--all-effects', '-ae', action='store_true', help='生成指定框架下全部色彩效果')
    parser.add_argument('--all', '-a', action='store_true', help='生成所有可能组合')
    parser.add_argument('--random', '-r', type=int, metavar='N', help='生成 N 个随机组合')
    parser.add_argument('--compress', '-c', nargs='?', const=True, help='压缩指定目录图片')
    parser.add_argument('--quality', '-q', type=int, default=85, help='压缩质量')
    parser.add_argument('--convert', choices=['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tif', 'tiff'], help='转换 images/input 内图片格式')
    parser.add_argument('--input-dir', default=str(DEFAULT_INPUT_DIR), help='输入目录')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR), help='输出目录')
    parser.add_argument('--title', default='', help='Polaroid 照片标题')
    parser.add_argument('--signature', default='', help='Polaroid 版权署名')
    parser.add_argument('--timestamp', default='', help='Polaroid 时间戳')
    parser.add_argument('--note', default='', help='Polaroid 备注')
    args = parser.parse_args(argv)

    ensure_dirs()
    if args.interactive:
        interactive_menu()
        return 0
    if args.convert:
        return 0 if convert_images_format(args.convert, input_dir=Path(args.input_dir)) else 1
    if args.compress:
        target = Path(args.input_dir) if args.compress is True else Path(args.compress)
        return 0 if compress_directory_images(target, args.quality) else 1

    ts = normalize_timestamp(args.timestamp)
    if ts is None:
        safe_print('时间格式错误。示例: 2026.04.12 或 2026.04.12 18:30')
        return 2

    kwargs = dict(input_dir=Path(args.input_dir), output_dir=Path(args.output_dir), title=args.title, signature=args.signature, timestamp=ts, note=args.note)
    if args.all:
        ok = generate_all_combinations(**kwargs)
    elif args.random:
        ok = generate_random_combinations(args.random, **kwargs)
    elif args.all_effects:
        ok = generate_styles(args.frame, STYLE_EFFECTS, **kwargs)
    else:
        effects = args.effects if args.effects is not None else [None]
        ok = generate_styles(args.frame, effects, **kwargs)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
