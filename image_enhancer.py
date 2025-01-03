from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import numpy as np
from abc import ABC, abstractmethod
import os

class StyleProcessor(ABC):
    """样式处理器基类"""
    def __init__(self, image):
        """初始化样式处理器
        
        Args:
            image (PIL.Image): 要处理的图片
            
        Raises:
            ValueError: 当输入不是有效的PIL.Image对象时
        """
        if not isinstance(image, Image.Image):
            raise ValueError("输入必须是PIL.Image对象")
        self.original_image = image
    
    @abstractmethod
    def process(self):
        """处理图片并返回处理后的图片"""
        pass
    
    def apply_grain_effect(self, image, intensity=5, blend=0.03):
        """应用颗粒感效果（性能优化版本）"""
        try:
            # 使用 numpy 批量生成噪声，避免逐像素操作
            width, height = image.size
            noise = np.random.normal(0, intensity, (height, width, 3))
            noise = np.clip(128 + noise, 0, 255).astype(np.uint8)
            grain = Image.fromarray(noise)
            
            return Image.blend(image, grain, blend)
        except Exception as e:
            raise RuntimeError(f"应用颗粒感效果时出错: {str(e)}")

class ImageEnhancer:
    """图片增强器主类"""
    def __init__(self, input_path):
        """初始化图片增强器"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
        # 添加文件格式验证
        if not input_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValueError("仅支持 JPG 和 PNG 格式的图片")
            
        try:
            self.image = Image.open(input_path)
        except Exception as e:
            raise ValueError(f"无法打开图片文件: {str(e)}")
            
        self.original_mode = self.image.mode
        if self.original_mode not in ['RGB', 'RGBA']:
            self.image = self.image.convert('RGB')
    
    def apply_style(self, style_name, output_path):
        """应用指定的样式并保存（性能优化版本）"""
        if not style_name:
            raise ValueError("样式名称不能为空")
        if not output_path:
            raise ValueError("输出路径不能为空")
            
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n正在处理: {style_name}")
        print("1. 加载图片...")
        
        # 解析样式名称
        parts = style_name.split('_', 1)
        frame_style = parts[0]
        color_style = parts[1] if len(parts) > 1 else None
        
        # 框架处理器映射
        frame_processors = {
            'original': lambda img: OriginalStyle(img),
            'polaroid': lambda img: PolaroidStyle(img, vintage_effect=False),
            'symmetric': lambda img: SymmetricPolaroidStyle(img, vintage_effect=False)
        }
        
        # 色彩处理器映射
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
            'retro_80s': lambda img: RetroColorStyle(img, decade='1980s')
        }
        
        processed_image = self.image
        
        # 如果需要应用色彩效果，先转换为numpy数组进行处理
        if color_style:
            print(f"2. 应用{color_style}色彩效果...")
            # 转换为numpy数组
            img_array = np.array(processed_image)
            
            # 应用色彩效果
            color_processor = color_processors.get(color_style)
            if not color_processor:
                raise ValueError(f"不支持的色彩风格: {color_style}")
            processor = color_processor(Image.fromarray(img_array))
            processed_image = processor.process()
        
        # 应用框架效果
        print(f"3. 应用{frame_style}框架...")
        frame_processor = frame_processors.get(frame_style)
        if not frame_processor:
            raise ValueError(f"不支持的框架风格: {frame_style}")
        
        final_image = frame_processor(processed_image).process()
        
        # 优化保存过程
        print("4. 保存结果...")
        try:
            final_image.save(
                output_path, 
                'JPEG',
                quality=95,  # 稍微降低质量以提高性能
                optimize=True,  # 启用优化
                progressive=True  # 使用渐进式JPEG
            )
            print("处理完成！")
        except Exception as e:
            raise IOError(f"保存图片时出错: {str(e)}")

    @staticmethod
    def get_supported_styles():
        """获取所有支持的样式"""
        return {
            'frames': ['original', 'polaroid', 'symmetric'],
            'effects': [
                'vintage',
                'bw_classic', 'bw_high_contrast', 'bw_soft',
                'instant_70s', 'instant_80s', 'instant_90s',
                'cross_process', 'cross_light', 'cross_strong',
                'cinematic_kodak', 'cinematic_fuji', 'cinematic_vision3',
                'retro_60s', 'retro_70s', 'retro_80s'
            ]
        }

class VintageEffect(StyleProcessor):
    """复古效果处理器"""
    def process(self):
        """应用复古效果（性能优化版本）"""
        # 转换为numpy数组进行处理
        img_array = np.array(self.original_image)
        
        # 一次性调整RGB通道
        img_array = img_array.astype(np.float32)
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.05, 0, 255)  # R
        img_array[:, :, 2] = img_array[:, :, 2] * 0.95  # B
        
        image = Image.fromarray(img_array.astype(np.uint8))
        
        # 其他增强操作
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.65)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(0.85)
        
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        return self.apply_grain_effect(image)

class BWFilmStyle(StyleProcessor):
    """黑白胶片效果处理器"""
    def __init__(self, image, film_type='classic'):
        super().__init__(image)
        self.film_type = film_type
    
    def process(self):
        """应用黑白胶片效果"""
        image = self.original_image.convert('L')  # 转换为灰度图
        
        # 根据不同类型应用不同的对比度
        contrast_map = {
            'classic': 1.1,      # 经典黑白
            'high_contrast': 1.5, # 高对比度
            'soft': 0.9          # 柔和效果
        }
        
        contrast = contrast_map.get(self.film_type, 1.1)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # 转回RGB模式并添加颗粒感
        return self.apply_grain_effect(image.convert('RGB'))

class InstantStyle(StyleProcessor):
    """即时显影效果处理器"""
    def __init__(self, image, era='80s'):
        super().__init__(image)
        self.era = era
    
    def process(self):
        """应用即时显影效果"""
        image = self.original_image.copy()
        
        # 不同年代的色彩特点
        era_settings = {
            '70s': {'saturation': 1.2, 'warmth': 0.9, 'green_tint': 1.1},
            '80s': {'saturation': 1.3, 'warmth': 1.1, 'green_tint': 1.0},
            '90s': {'saturation': 1.1, 'warmth': 1.0, 'green_tint': 1.0}
        }
        
        settings = era_settings.get(self.era, era_settings['80s'])
        
        # 调整饱和度
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(settings['saturation'])
        
        # 调整色温和色调
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        g = g.point(lambda i: min(int(i * settings['green_tint']), 255))
        image = Image.merge('RGB', (r, g, b))
        
        return self.apply_grain_effect(image)

class CrossProcessStyle(StyleProcessor):
    """交叉冲洗效果处理器"""
    def __init__(self, image, intensity=1.0):
        super().__init__(image)
        self.intensity = intensity
    
    def process(self):
        """应用交叉冲洗效果"""
        image = self.original_image.copy()
        
        # 增强对比度和饱和度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + 0.3 * self.intensity)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0 + 0.4 * self.intensity)
        
        # 调整色调
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * (1.0 + 0.1 * self.intensity)), 255))
        b = b.point(lambda i: min(int(i * (1.0 - 0.1 * self.intensity)), 255))
        image = Image.merge('RGB', (r, g, b))
        
        return self.apply_grain_effect(image)

class CinematicStyle(StyleProcessor):
    """电影胶片效果处理器"""
    def __init__(self, image, stock='kodak'):
        super().__init__(image)
        self.stock = stock
    
    def process(self):
        """应用电影胶片效果"""
        image = self.original_image.copy()
        
        # 不同胶片的特性
        stock_settings = {
            'kodak': {'contrast': 1.2, 'saturation': 1.1, 'warmth': 1.1},
            'fuji': {'contrast': 1.1, 'saturation': 1.2, 'warmth': 0.95},
            'vision3': {'contrast': 1.15, 'saturation': 1.05, 'warmth': 1.0}
        }
        
        settings = stock_settings.get(self.stock, stock_settings['kodak'])
        
        # 应用效果
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(settings['contrast'])
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(settings['saturation'])
        
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        image = Image.merge('RGB', (r, g, b))
        
        return self.apply_grain_effect(image)

class RetroColorStyle(StyleProcessor):
    """复古彩色效果处理器"""
    def __init__(self, image, decade='1980s'):
        super().__init__(image)
        self.decade = decade
    
    def process(self):
        """应用复古彩色效果"""
        image = self.original_image.copy()
        
        # 不同年代的色彩特点
        decade_settings = {
            '1960s': {'saturation': 1.4, 'contrast': 1.2, 'warmth': 1.1},
            '1970s': {'saturation': 1.2, 'contrast': 1.1, 'warmth': 1.2},
            '1980s': {'saturation': 1.3, 'contrast': 1.15, 'warmth': 1.05}
        }
        
        settings = decade_settings.get(self.decade, decade_settings['1980s'])
        
        # 应用效果
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(settings['saturation'])
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(settings['contrast'])
        
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * settings['warmth']), 255))
        image = Image.merge('RGB', (r, g, b))
        
        return self.apply_grain_effect(image)

class PolaroidStyle(StyleProcessor):
    """拍立得框架处理器"""
    def __init__(self, image, vintage_effect=False):
        super().__init__(image)
        self.vintage_effect = vintage_effect
    
    def process(self):
        """应用拍立得框架效果"""
        # 计算框架尺寸
        original_width = self.original_image.width
        original_height = self.original_image.height
        
        # 使用固定比例计算边框尺寸
        side_margin = int(original_width * 0.075)   # 7.5% of width
        top_margin = int(original_width * 0.075)    # 7.5% of width
        bottom_margin = int(original_height * 0.14)  # 14% of height
        
        # 计算最终尺寸
        frame_width = original_width + (side_margin * 2)
        frame_height = original_height + top_margin + bottom_margin
        
        # 创建白色背景
        frame = Image.new('RGB', (frame_width, frame_height), 'white')
        
        # 粘贴原图到框架中心
        paste_x = side_margin
        paste_y = top_margin
        frame.paste(self.original_image, (paste_x, paste_y))
        
        # 添加轻微的阴影效果
        shadow = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # 在图片周围画一个非常淡的灰色边框
        shadow_draw.rectangle(
            [paste_x-1, paste_y-1, 
             paste_x+original_width+1, paste_y+original_height+1],
            outline=(128, 128, 128, 30)
        )
        
        # 将阴影混合到框架上
        frame = Image.alpha_composite(frame.convert('RGBA'), shadow).convert('RGB')
        
        return frame

class SymmetricPolaroidStyle(StyleProcessor):
    """对称边框处理器"""
    def __init__(self, image, vintage_effect=False):
        super().__init__(image)
        self.vintage_effect = vintage_effect
    
    def process(self):
        """应用对称边框效果"""
        # 计算框架尺寸
        original_width = self.original_image.width
        original_height = self.original_image.height
        
        # 使用固定比例计算边框尺寸（四边相等）
        margin = int(original_width * 0.1)  # 10% of width
        
        # 计算最终尺寸
        frame_width = original_width + (margin * 2)
        frame_height = original_height + (margin * 2)
        
        # 创建白色背景
        frame = Image.new('RGB', (frame_width, frame_height), 'white')
        
        # 粘贴原图到框架中心
        paste_x = margin
        paste_y = margin
        frame.paste(self.original_image, (paste_x, paste_y))
        
        # 添加轻微的阴影效果
        shadow = Image.new('RGBA', frame.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # 在图片周围画一个非常淡的灰色边框
        shadow_draw.rectangle(
            [paste_x-1, paste_y-1, 
             paste_x+original_width+1, paste_y+original_height+1],
            outline=(128, 128, 128, 30)
        )
        
        # 将阴影混合到框架上
        frame = Image.alpha_composite(frame.convert('RGBA'), shadow).convert('RGB')
        
        return frame

class OriginalStyle(StyleProcessor):
    """原始风格处理器（无边框）"""
    def process(self):
        """直接返回原始图片"""
        return self.original_image

@staticmethod
def get_supported_styles():
    """获取所有支持的样式
    
    Returns:
        dict: 包含所有支持的框架和效果
            {
                'frames': [...],
                'effects': [...]
            }
    """
    return {
        'frames': ['original', 'polaroid', 'symmetric'],
        'effects': [
            'vintage',
            'bw_classic', 'bw_high_contrast', 'bw_soft',
            'instant_70s', 'instant_80s', 'instant_90s',
            'cross_process', 'cross_light', 'cross_strong',
            'cinematic_kodak', 'cinematic_fuji', 'cinematic_vision3',
            'retro_60s', 'retro_70s', 'retro_80s'
        ]
    } 