# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')


class StyleProcessor(ABC):
    def __init__(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise ValueError('输入必须是PIL.Image对象')
        self.original_image = image.convert('RGB')

    @abstractmethod
    def process(self) -> Image.Image:
        pass

    def apply_grain_effect(self, image: Image.Image, intensity: int = 5, blend: float = 0.03) -> Image.Image:
        width, height = image.size
        noise = np.random.normal(0, intensity, (height, width, 3))
        noise = np.clip(128 + noise, 0, 255).astype(np.uint8)
        grain = Image.fromarray(noise, mode='RGB')
        return Image.blend(image.convert('RGB'), grain, blend)


class ImageEnhancer:
    def __init__(self, input_path: str | os.PathLike[str]):
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f'输入文件不存在: {self.input_path}')
        if self.input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError('仅支持 JPG/JPEG/PNG/WEBP/BMP/TIF/TIFF 格式的图片')
        try:
            with Image.open(self.input_path) as img:
                self.image = img.convert('RGB')
        except Exception as e:
            raise ValueError(f'无法打开图片文件: {e}')

    def apply_style(
        self,
        style_name: str,
        output_path: str | os.PathLike[str],
        *,
        title: str = '',
        signature: str = '',
        timestamp: str = '',
        note: str = '',
    ) -> None:
        if not style_name:
            raise ValueError('样式名称不能为空')

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f'\n正在处理: {style_name}')
        print('1. 加载图片...')

        parts = style_name.split('_', 1)
        frame_style = parts[0]
        color_style = parts[1] if len(parts) > 1 else None

        frame_processors = {
            'original': lambda img: OriginalStyle(img),
            'polaroid': lambda img: PolaroidStyle(
                img,
                title=title,
                signature=signature,
                timestamp=timestamp,
                note=note,
            ),
            'symmetric': lambda img: SymmetricPolaroidStyle(img),
        }
        color_processors = {
            'vintage': lambda img: VintageEffect(img),
            'bw_classic': lambda img: BWFilmStyle(img, film_type='classic'),
            'bw_high_contrast': lambda img: BWFilmStyle(img, film_type='high_contrast'),
            'bw_soft': lambda img: BWFilmStyle(img, film_type='soft'),
            'instant_70s': lambda img: InstantStyle(img, era='70s'),
            'instant_80s': lambda img: InstantStyle(img, era='80s'),
            'instant_90s': lambda img: InstantStyle(img, era='90s'),
            'cross_process': lambda img: CrossProcessStyle(img, intensity=1.0),
            'cross_light': lambda img: CrossProcessStyle(img, intensity=0.7),
            'cross_strong': lambda img: CrossProcessStyle(img, intensity=1.3),
            'cinematic_kodak': lambda img: CinematicStyle(img, stock='kodak'),
            'cinematic_fuji': lambda img: CinematicStyle(img, stock='fuji'),
            'cinematic_vision3': lambda img: CinematicStyle(img, stock='vision3'),
            'retro_60s': lambda img: RetroColorStyle(img, decade='1960s'),
            'retro_70s': lambda img: RetroColorStyle(img, decade='1970s'),
            'retro_80s': lambda img: RetroColorStyle(img, decade='1980s'),
        }

        processed_image = self.image
        if color_style:
            print(f'2. 应用 {color_style} 色彩效果...')
            color_processor = color_processors.get(color_style)
            if not color_processor:
                raise ValueError(f'不支持的色彩风格: {color_style}')
            processed_image = color_processor(processed_image).process()

        print(f'3. 应用 {frame_style} 框架...')
        frame_processor = frame_processors.get(frame_style)
        if not frame_processor:
            raise ValueError(f'不支持的框架风格: {frame_style}')
        final_image = frame_processor(processed_image).process()

        print('4. 保存结果...')
        save_image_keep_extension(final_image, output_path)
        print('处理完成！')

    @staticmethod
    def get_supported_styles() -> dict:
        return {
            'frames': ['original', 'polaroid', 'symmetric'],
            'effects': [
                'vintage', 'bw_classic', 'bw_high_contrast', 'bw_soft',
                'instant_70s', 'instant_80s', 'instant_90s',
                'cross_process', 'cross_light', 'cross_strong',
                'cinematic_kodak', 'cinematic_fuji', 'cinematic_vision3',
                'retro_60s', 'retro_70s', 'retro_80s',
            ],
        }


def save_image_keep_extension(image: Image.Image, output_path: Path) -> None:
    ext = output_path.suffix.lower()
    img = image.convert('RGB')
    if ext in ('.jpg', '.jpeg'):
        img.save(output_path, 'JPEG', quality=95, optimize=True, progressive=True)
    elif ext == '.png':
        img.save(output_path, 'PNG', optimize=True)
    elif ext == '.webp':
        img.save(output_path, 'WEBP', quality=95, method=6)
    elif ext == '.bmp':
        img.save(output_path, 'BMP')
    elif ext in ('.tif', '.tiff'):
        img.save(output_path, 'TIFF', compression='tiff_lzw')
    else:
        img.save(output_path.with_suffix('.jpg'), 'JPEG', quality=95, optimize=True)


class VintageEffect(StyleProcessor):
    def process(self):
        arr = np.array(self.original_image).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.95, 0, 255)
        image = Image.fromarray(arr.astype(np.uint8), mode='RGB')
        image = ImageEnhance.Color(image).enhance(0.65)
        image = ImageEnhance.Contrast(image).enhance(0.85)
        image = ImageEnhance.Brightness(image).enhance(1.1)
        return self.apply_grain_effect(image)


class BWFilmStyle(StyleProcessor):
    def __init__(self, image, film_type='classic'):
        super().__init__(image)
        self.film_type = film_type

    def process(self):
        image = self.original_image.convert('L')
        contrast = {'classic': 1.1, 'high_contrast': 1.5, 'soft': 0.9}.get(self.film_type, 1.1)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        return self.apply_grain_effect(image.convert('RGB'))


class InstantStyle(StyleProcessor):
    def __init__(self, image, era='80s'):
        super().__init__(image)
        self.era = era

    def process(self):
        image = self.original_image.copy()
        settings = {
            '70s': {'saturation': 1.2, 'warmth': 0.9, 'green_tint': 1.1},
            '80s': {'saturation': 1.3, 'warmth': 1.1, 'green_tint': 1.0},
            '90s': {'saturation': 1.1, 'warmth': 1.0, 'green_tint': 1.0},
        }.get(self.era, {'saturation': 1.3, 'warmth': 1.1, 'green_tint': 1.0})
        image = ImageEnhance.Color(image).enhance(settings['saturation'])
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        g = g.point(lambda i: min(int(i * settings['green_tint']), 255))
        return self.apply_grain_effect(Image.merge('RGB', (r, g, b)))


class CrossProcessStyle(StyleProcessor):
    def __init__(self, image, intensity=1.0):
        super().__init__(image)
        self.intensity = intensity

    def process(self):
        image = self.original_image.copy()
        image = ImageEnhance.Contrast(image).enhance(1.0 + 0.3 * self.intensity)
        image = ImageEnhance.Color(image).enhance(1.0 + 0.4 * self.intensity)
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * (1.0 + 0.1 * self.intensity)), 255))
        b = b.point(lambda i: min(int(i * (1.0 - 0.1 * self.intensity)), 255))
        return self.apply_grain_effect(Image.merge('RGB', (r, g, b)))


class CinematicStyle(StyleProcessor):
    def __init__(self, image, stock='kodak'):
        super().__init__(image)
        self.stock = stock

    def process(self):
        image = self.original_image.copy()
        settings = {
            'kodak': {'contrast': 1.2, 'saturation': 1.1, 'warmth': 1.1},
            'fuji': {'contrast': 1.1, 'saturation': 1.2, 'warmth': 0.95},
            'vision3': {'contrast': 1.15, 'saturation': 1.05, 'warmth': 1.0},
        }.get(self.stock, {'contrast': 1.2, 'saturation': 1.1, 'warmth': 1.1})
        image = ImageEnhance.Contrast(image).enhance(settings['contrast'])
        image = ImageEnhance.Color(image).enhance(settings['saturation'])
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        return self.apply_grain_effect(Image.merge('RGB', (r, g, b)))


class RetroColorStyle(StyleProcessor):
    def __init__(self, image, decade='1980s'):
        super().__init__(image)
        self.decade = decade

    def process(self):
        image = self.original_image.copy()
        settings = {
            '1960s': {'saturation': 1.4, 'contrast': 1.2, 'warmth': 1.1},
            '1970s': {'saturation': 1.2, 'contrast': 1.1, 'warmth': 1.2},
            '1980s': {'saturation': 1.3, 'contrast': 1.15, 'warmth': 1.05},
        }.get(self.decade, {'saturation': 1.3, 'contrast': 1.15, 'warmth': 1.05})
        image = ImageEnhance.Color(image).enhance(settings['saturation'])
        image = ImageEnhance.Contrast(image).enhance(settings['contrast'])
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        return self.apply_grain_effect(Image.merge('RGB', (r, g, b)))


class PolaroidStyle(StyleProcessor):
    def __init__(self, image, *, title='', signature='', timestamp='', note=''):
        super().__init__(image)
        self.title = (title or '').strip()
        self.signature = (signature or '').strip()
        self.timestamp = (timestamp or '').strip()
        self.note = (note or '').strip()

    def process(self):
        original_width = self.original_image.width
        original_height = self.original_image.height
        side_margin = max(1, int(original_width * 0.075))
        top_margin = max(1, int(original_width * 0.075))
        bottom_margin = max(92, int(original_height * 0.145))

        frame_width = original_width + side_margin * 2
        frame_height = original_height + top_margin + bottom_margin
        frame = Image.new('RGB', (frame_width, frame_height), 'white')
        paste_x = side_margin
        paste_y = top_margin
        frame.paste(self.original_image, (paste_x, paste_y))

        shadow = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle(
            [paste_x - 1, paste_y - 1, paste_x + original_width + 1, paste_y + original_height + 1],
            outline=(128, 128, 128, 26),
        )
        frame = Image.alpha_composite(frame.convert('RGBA'), shadow).convert('RGB')
        self._draw_text_area(frame, paste_x, paste_y, original_width, original_height, bottom_margin)
        return frame

    def _draw_text_area(self, frame, photo_x, photo_y, photo_w, photo_h, bottom_margin):
        if not any([self.title, self.signature, self.timestamp, self.note]):
            return
        helper = Path(__file__).resolve().with_name('annotation_worker.py')
        if not helper.exists():
            print('警告：缺少 annotation_worker.py，已跳过文字信息区。')
            return

        payload = {
            'frame_width': frame.width,
            'frame_height': frame.height,
            'photo_x': photo_x,
            'photo_y': photo_y,
            'photo_width': photo_w,
            'photo_height': photo_h,
            'bottom_margin': bottom_margin,
            'title': self.title,
            'signature': self.signature,
            'timestamp': self.timestamp,
            'note': self.note,
            'title_color': '#555555',
            'signature_color': '#707070',
            'date_color': '#666666',
            'note_color': '#777777',
            'divider_color': '#B8B8B8',
            'title_size_ratio': 0.047,
            'body_size_ratio': 0.020,
            'date_size_ratio': 0.018,
            'note_size_ratio': 0.018,
            'show_divider': True,
        }

        pairs = self._font_pairs()
        if not pairs:
            print('警告：未找到可用字体，已跳过文字信息区。')
            return

        with tempfile.TemporaryDirectory(prefix='polaroid_text_') as tmpdir:
            tmp = Path(tmpdir)
            payload_path = tmp / 'payload.json'
            overlay_path = tmp / 'overlay.png'
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

            for title_font, body_font in pairs:
                cmd = [
                    sys.executable,
                    str(helper),
                    '--payload', str(payload_path),
                    '--output', str(overlay_path),
                    '--title-font', str(title_font),
                    '--body-font', str(body_font),
                ]
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if result.returncode == 0 and overlay_path.exists():
                    try:
                        with Image.open(overlay_path) as overlay_img:
                            overlay = overlay_img.convert('RGBA')
                            composed = frame.convert('RGBA')
                            composed.alpha_composite(overlay)
                            frame.paste(composed.convert('RGB'))
                            return
                    except Exception:
                        continue
        print('警告：文字信息区渲染失败，已跳过该文字区，不影响图片输出。')

    @staticmethod
    def _existing(paths):
        result = []
        for p in paths:
            path = Path(p)
            if path.exists() and path.is_file():
                result.append(path)
        return result

    @classmethod
    def _font_pairs(cls):
        # CJK serif-like fonts for title. Use real file paths only; never rely on PIL default font for CJK.
        title_candidates = cls._existing([
            # Windows Japanese / Chinese serif first
            'C:/Windows/Fonts/yuminl.ttf',
            'C:/Windows/Fonts/yumin.ttf',
            'C:/Windows/Fonts/YuMincho.ttc',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msgothic.ttc',
            'C:/Windows/Fonts/msmincho.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            # macOS
            '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Supplemental/Songti.ttc',
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            # Linux
            '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        ])
        body_candidates = cls._existing([
            # Windows sans
            'C:/Windows/Fonts/segoeui.ttf',
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/meiryo.ttc',
            'C:/Windows/Fonts/YuGothR.ttc',
            # macOS
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/System/Library/Fonts/PingFang.ttc',
            # Linux
            '/usr/share/fonts/opentype/inter/Inter-Light.otf',
            '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
        ])
        if not title_candidates or not body_candidates:
            return []
        pairs = []
        # Try each title font with best body font first, then more combinations if needed.
        for t in title_candidates:
            for b in body_candidates[:4]:
                pairs.append((t, b))
        return pairs


class SymmetricPolaroidStyle(StyleProcessor):
    def process(self):
        original_width = self.original_image.width
        original_height = self.original_image.height
        margin = max(1, int(original_width * 0.10))
        frame = Image.new('RGB', (original_width + margin * 2, original_height + margin * 2), 'white')
        frame.paste(self.original_image, (margin, margin))
        shadow = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        draw.rectangle([margin - 1, margin - 1, margin + original_width + 1, margin + original_height + 1], outline=(128, 128, 128, 26))
        return Image.alpha_composite(frame.convert('RGBA'), shadow).convert('RGB')


class OriginalStyle(StyleProcessor):
    def process(self):
        return self.original_image.convert('RGB')
