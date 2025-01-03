from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import numpy as np
from abc import ABC, abstractmethod

class StyleProcessor(ABC):
    """样式处理器基类"""
    def __init__(self, image):
        self.original_image = image
    
    @abstractmethod
    def process(self):
        """处理图片并返回处理后的图片"""
        pass
    
    def apply_grain_effect(self, image, intensity=5, blend=0.03):
        """应用颗粒感效果
        
        Args:
            image (PIL.Image): 要处理的图片
            intensity (int): 颗粒感强度，默认5
            blend (float): 混合比例，默认0.03
            
        Returns:
            PIL.Image: 添加颗粒感后的图片
        """
        grain = Image.new('RGB', image.size, (128, 128, 128))
        for x in range(image.width):
            for y in range(image.height):
                noise = int(np.random.normal(0, intensity))
                grain.putpixel((x, y), (128+noise, 128+noise, 128+noise))
        
        return Image.blend(image, grain, blend)

class PolaroidStyle(StyleProcessor):
    """拍立得风格处理器基类"""
    def __init__(self, image, vintage_effect=True):
        super().__init__(image)
        self.vintage_effect = vintage_effect
    
    def calculate_frame_size(self):
        """计算拍立得相框尺寸，保持原图分辨率不变
        
        拍立得相框规格（基于实际拍立得照片尺寸比例）：
        - 边框颜色：纯白色
        - 左右边框：原图宽度的 7.5%
        - 顶部边框：原图宽度的 7.5%
        - 底部边框：原图高度的 14%
        """
        original_width = self.original_image.width
        original_height = self.original_image.height
        
        # 使用固定比例计算边框尺寸（基于原图尺寸）
        side_margin = int(original_width * 0.075)   # 7.5% of width
        top_margin = int(original_width * 0.075)    # 7.5% of width
        bottom_margin = int(original_height * 0.14)  # 14% of height
        
        # 计算最终尺寸（原图尺寸 + 边框）
        frame_width = original_width + (side_margin * 2)
        frame_height = original_height + top_margin + bottom_margin
        
        return (frame_width, frame_height), (side_margin, top_margin)
    
    def apply_vintage_effect(self, image):
        """应用褪色的复古效果"""
        image = image.copy()
        
        # 1. 降低饱和度（模拟褪色）
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.65)  # 显著降低饱和度
        
        # 2. 轻微降低对比度（模拟老照片）
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(0.85)
        
        # 3. 轻微调整色温（略微偏暖）
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * 1.05), 255))  # 轻微增加红色
        b = b.point(lambda i: int(i * 0.95))  # 轻微降低蓝色
        image = Image.merge('RGB', (r, g, b))
        
        # 4. 轻微提亮（模拟曝光）
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        # 5. 添加细腻的颗粒感
        image = self.apply_grain_effect(image, intensity=5, blend=0.03)
        
        return image
    
    def process(self):
        """处理图片为拍立得风格"""
        frame_size, (margin_x, margin_y) = self.calculate_frame_size()
        
        # 创建纯白色框架
        frame = Image.new('RGB', frame_size, (255, 255, 255))
        
        if self.vintage_effect:
            # 复古效果版本
            processed_image = self.apply_vintage_effect(self.original_image)
            frame.paste(processed_image, (margin_x, margin_y))
        else:
            # 原色版本
            frame.paste(self.original_image, (margin_x, margin_y))
        
        return frame

class SymmetricPolaroidStyle(PolaroidStyle):
    """对称边框的拍立得风格处理器"""
    def calculate_frame_size(self):
        """计算相框尺寸，四边等宽，保持原图分辨率不变
        
        拍立得相框规格（基于实际拍立得照片尺寸比例）：
        - 边框颜色：纯白色
        - 四边边框：原图宽度的 7.5%（保持一致的边距）
        """
        original_width = self.original_image.width
        original_height = self.original_image.height
        
        # 使用固定比例计算边框尺寸（基于原图尺寸）
        margin = int(original_width * 0.075)  # 7.5% of width
        
        # 计算最终尺寸（原图尺寸 + 边框）
        frame_width = original_width + (margin * 2)
        frame_height = original_height + (margin * 2)
        
        return (frame_width, frame_height), (margin, margin)
    
    def process(self):
        """处理图片为对称边框的拍立得风格"""
        frame_size, (margin_x, margin_y) = self.calculate_frame_size()
        
        # 创建纯白色框架
        frame = Image.new('RGB', frame_size, (255, 255, 255))
        
        if self.vintage_effect:
            # 复古效果版本
            processed_image = self.apply_vintage_effect(self.original_image)
            frame.paste(processed_image, (margin_x, margin_y))
        else:
            # 原色版本
            frame.paste(self.original_image, (margin_x, margin_y))
        
        return frame

class BWFilmStyle(StyleProcessor):
    """黑白胶片风格处理器"""
    def __init__(self, image, film_type='classic'):
        super().__init__(image)
        self.film_type = film_type
    
    def apply_bw_effect(self, image):
        """应用黑白效果"""
        # 转换为黑白
        image = image.convert('L')
        image = image.convert('RGB')
        
        # 根据不同的胶片类型调整效果
        enhancer = ImageEnhance.Contrast(image)
        if self.film_type == 'high_contrast':
            # 高对比度版本
            image = enhancer.enhance(1.5)
        elif self.film_type == 'soft':
            # 柔和版本
            image = enhancer.enhance(0.8)
            # 增加亮度
            bright = ImageEnhance.Brightness(image)
            image = bright.enhance(1.2)
        else:  # classic
            # 经典版本
            image = enhancer.enhance(1.2)
        
        # 添加胶片颗粒感（黑白胶片的颗粒感通常更强）
        image = self.apply_grain_effect(image, intensity=8, blend=0.05)
        
        return image
    
    def process(self):
        """处理图片为黑白胶片风格"""
        # 处理图片
        processed_image = self.apply_bw_effect(self.original_image)
        return processed_image

class InstantStyle(StyleProcessor):
    """即时显影风格处理器"""
    def __init__(self, image, era='70s'):
        super().__init__(image)
        self.era = era
    
    def apply_instant_effect(self, image):
        """应用即时显影效果"""
        image = image.copy()
        
        # 基础调整
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # 根据年代应用不同的色彩效果
        r, g, b = image.split()
        if self.era == '70s':
            # 70年代风格（偏绿色调）
            g = g.point(lambda i: min(int(i * 1.1), 255))
            b = b.point(lambda i: int(i * 0.9))
        elif self.era == '80s':
            # 80年代风格（偏暖色调）
            r = r.point(lambda i: min(int(i * 1.15), 255))
            b = b.point(lambda i: int(i * 0.85))
        else:  # 90s
            # 90年代风格（更自然的色彩）
            r = r.point(lambda i: min(int(i * 1.05), 255))
            g = g.point(lambda i: min(int(i * 1.02), 255))
        
        image = Image.merge('RGB', (r, g, b))
        
        # 调整对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # 添加轻微的颗粒感
        image = self.apply_grain_effect(image, intensity=4, blend=0.03)
        
        return image
    
    def process(self):
        """处理图片为即时显影风格"""
        # 处理图片
        processed_image = self.apply_instant_effect(self.original_image)
        return processed_image

class CrossProcessStyle(StyleProcessor):
    """交叉冲洗效果处理器"""
    def __init__(self, image, intensity=1.0):
        super().__init__(image)
        self.intensity = intensity
    
    def apply_cross_process(self, image):
        """应用交叉冲洗效果"""
        image = image.copy()
        
        # 增强饱和度
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
        
        # 调整色彩通道
        r, g, b = image.split()
        
        # 红色通道：增强高光，压暗阴影
        r = r.point(lambda i: min(int(i * 1.2), 255) if i > 128 else int(i * 0.8))
        
        # 绿色通道：轻微增强
        g = g.point(lambda i: min(int(i * 1.1), 255))
        
        # 蓝色通道：强化高光区域
        b = b.point(lambda i: min(int(i * 1.5), 255) if i > 128 else i)
        
        # 合并通道
        image = Image.merge('RGB', (r, g, b))
        
        # 增加对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.4)
        
        # 根据强度混合效果
        image = Image.blend(self.original_image, image, self.intensity)
        
        # 添加颗粒感
        image = self.apply_grain_effect(image, intensity=6, blend=0.05)
        
        return image
    
    def process(self):
        """处理图片为交叉冲洗风格"""
        return self.apply_cross_process(self.original_image)

class CinematicStyle(StyleProcessor):
    """电影胶片效果处理器"""
    def __init__(self, image, stock='kodak'):
        super().__init__(image)
        self.stock = stock
    
    def apply_cinematic_effect(self, image):
        """应用电影胶片效果"""
        image = image.copy()
        
        # 基础色彩调整
        r, g, b = image.split()
        
        if self.stock == 'kodak':
            # 柯达风格：温暖的色调，偏黄色
            r = r.point(lambda i: min(int(i * 1.1), 255))
            g = g.point(lambda i: min(int(i * 1.05), 255))
            b = b.point(lambda i: int(i * 0.9))
        elif self.stock == 'fuji':
            # 富士风格：清爽的色调，偏绿色
            r = r.point(lambda i: int(i * 0.9))
            g = g.point(lambda i: min(int(i * 1.1), 255))
            b = b.point(lambda i: min(int(i * 1.05), 255))
        else:  # vision3
            # Vision3风格：自然的色调，宽容度高
            r = r.point(lambda i: min(int(i * 1.02), 255))
            g = g.point(lambda i: min(int(i * 1.02), 255))
            b = b.point(lambda i: min(int(i * 1.02), 255))
        
        image = Image.merge('RGB', (r, g, b))
        
        # 调整对比度和饱和度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.95)
        
        # 添加电影颗粒感（更细腻的颗粒）
        image = self.apply_grain_effect(image, intensity=3, blend=0.03)
        
        return image
    
    def process(self):
        """处理图片为电影胶片风格"""
        return self.apply_cinematic_effect(self.original_image)

class RetroColorStyle(StyleProcessor):
    """复古彩色效果处理器"""
    def __init__(self, image, decade='1960s'):
        super().__init__(image)
        self.decade = decade
    
    def apply_retro_effect(self, image):
        """应用复古彩色效果"""
        image = image.copy()
        
        # 基础色彩调整
        r, g, b = image.split()
        
        if self.decade == '1960s':
            # 60年代：高饱和度，鲜艳的色彩
            # 增强红色和绿色
            r = r.point(lambda i: min(int(i * 1.2), 255))
            g = g.point(lambda i: min(int(i * 1.1), 255))
            image = Image.merge('RGB', (r, g, b))
            
            # 增强饱和度
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.4)
            
            # 调整对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
        elif self.decade == '1970s':
            # 70年代：偏黄色调，轻微褪色
            r = r.point(lambda i: min(int(i * 1.1), 255))
            g = g.point(lambda i: min(int(i * 1.1), 255))
            b = b.point(lambda i: int(i * 0.85))
            image = Image.merge('RGB', (r, g, b))
            
            # 降低饱和度
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.85)
            
        else:  # 1980s
            # 80年代：偏红色调，高对比度
            r = r.point(lambda i: min(int(i * 1.15), 255))
            b = b.point(lambda i: int(i * 0.9))
            image = Image.merge('RGB', (r, g, b))
            
            # 增加对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.25)
        
        # 添加年代特征的颗粒感
        if self.decade == '1960s':
            image = self.apply_grain_effect(image, intensity=4, blend=0.04)
        elif self.decade == '1970s':
            image = self.apply_grain_effect(image, intensity=6, blend=0.04)
        else:  # 1980s
            image = self.apply_grain_effect(image, intensity=3, blend=0.04)
        
        # 轻微调整亮度
        enhancer = ImageEnhance.Brightness(image)
        if self.decade == '1970s':
            image = enhancer.enhance(1.1)  # 70年代略微提亮
        elif self.decade == '1980s':
            image = enhancer.enhance(0.95)  # 80年代略微降低亮度
        
        return image
    
    def process(self):
        """处理图片为复古彩色风格"""
        return self.apply_retro_effect(self.original_image)

class VintageEffect(StyleProcessor):
    """复古效果处理器"""
    def process(self):
        return self.apply_vintage_effect(self.original_image)
    
    def apply_vintage_effect(self, image):
        """应用复古效果
        
        特点：
        1. 降低饱和度模拟褪色
        2. 轻微降低对比度模拟老照片
        3. 轻微偏暖的色温
        4. 轻微提亮模拟曝光
        5. 添加细腻的颗粒感
        """
        image = image.copy()
        
        # 1. 降低饱和度（模拟褪色）
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.65)
        
        # 2. 轻微降低对比度（模拟老照片）
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(0.85)
        
        # 3. 轻微调整色温（略微偏暖）
        r, g, b = image.split()
        r = r.point(lambda i: min(int(i * 1.05), 255))
        b = b.point(lambda i: int(i * 0.95))
        image = Image.merge('RGB', (r, g, b))
        
        # 4. 轻微提亮（模拟曝光）
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        # 5. 添加细腻的颗粒感
        image = self.apply_grain_effect(image, intensity=5, blend=0.03)
        
        return image

class ImageEnhancer:
    """图片增强器主类"""
    def __init__(self, input_path):
        self.image = Image.open(input_path)
        self.original_mode = self.image.mode
        if self.original_mode not in ['RGB', 'RGBA']:
            self.image = self.image.convert('RGB')
    
    def apply_style(self, style_name, output_path):
        """应用指定的样式并保存"""
        print(f"\n正在处理: {style_name}")
        print("1. 加载图片...")
        
        # 解析样式名称
        parts = style_name.split('_', 1)
        frame_style = parts[0]
        color_style = parts[1] if len(parts) > 1 else None
        
        # 框架处理器映射
        frame_processors = {
            'original': lambda img: img,  # 无框架，直接返回原图
            'polaroid': lambda img: PolaroidStyle(img, vintage_effect=False),  # 拍立得框架
            'symmetric': lambda img: SymmetricPolaroidStyle(img, vintage_effect=False)  # 对称框架
        }
        
        # 色彩处理器映射
        color_processors = {
            # 复古效果
            'vintage': lambda img: VintageEffect(img),  # 直接使用 VintageEffect 类
            # 黑白效果
            'bw_classic': lambda img: BWFilmStyle(img, film_type='classic'),
            'bw_high_contrast': lambda img: BWFilmStyle(img, film_type='high_contrast'),
            'bw_soft': lambda img: BWFilmStyle(img, film_type='soft'),
            # 即时显影效果
            'instant_70s': lambda img: InstantStyle(img, era='70s'),
            'instant_80s': lambda img: InstantStyle(img, era='80s'),
            'instant_90s': lambda img: InstantStyle(img, era='90s'),
            # 交叉冲洗效果
            'cross_process': lambda img: CrossProcessStyle(img, intensity=1.0),
            'cross_light': lambda img: CrossProcessStyle(img, intensity=0.7),
            'cross_strong': lambda img: CrossProcessStyle(img, intensity=1.3),
            # 电影胶片效果
            'cinematic_kodak': lambda img: CinematicStyle(img, stock='kodak'),
            'cinematic_fuji': lambda img: CinematicStyle(img, stock='fuji'),
            'cinematic_vision3': lambda img: CinematicStyle(img, stock='vision3'),
            # 复古彩色效果
            'retro_60s': lambda img: RetroColorStyle(img, decade='1960s'),
            'retro_70s': lambda img: RetroColorStyle(img, decade='1970s'),
            'retro_80s': lambda img: RetroColorStyle(img, decade='1980s')
        }
        
        processed_image = self.image
        
        # 1. 首先应用色彩效果（如果有）
        if color_style:
            print(f"2. 应用{color_style}色彩效果...")
            color_processor = color_processors.get(color_style)
            if not color_processor:
                raise ValueError(f"不支持的色彩风格: {color_style}")
            processor = color_processor(processed_image)
            processed_image = processor.process()  # 使用 process 方法
        
        # 2. 然后应用框架效果
        print(f"3. 应用{frame_style}框架...")
        frame_processor = frame_processors.get(frame_style)
        if not frame_processor:
            raise ValueError(f"不支持的框架风格: {frame_style}")
        
        final_image = frame_processor(processed_image).process()
        
        # 3. 保存结果
        print("4. 保存结果...")
        final_image.save(output_path, quality=100, subsampling=0)
        
        print("处理完成！")
    
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