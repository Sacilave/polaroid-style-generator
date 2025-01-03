import os
from image_enhancer import ImageEnhancer

def process_image(input_path, output_path, frame_style, color_style=None):
    """处理图片的辅助函数
    
    Args:
        input_path (str): 输入图片路径
        output_path (str): 输出图片路径
        frame_style (str): 框架样式
        color_style (str, optional): 色彩风格
    """
    try:
        if not os.path.exists(input_path):
            print(f"错误：输入文件不存在: {input_path}")
            return

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        enhancer = ImageEnhancer(input_path)
        # 构建实际的样式名称
        if color_style:
            style_name = f"{frame_style}_{color_style}"
        else:
            style_name = frame_style
            
        enhancer.apply_style(style_name, output_path)
        print(f"处理完成！框架：{frame_style}，色彩：{color_style or '原色'}，输出文件：{output_path}")
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

def generate_styles(frame_style, color_styles=None):
    """根据框架样式和色彩风格生成效果"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(current_dir, "images", "input")
    output_dir = os.path.join(current_dir, "images", "output")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    input_image_path = os.path.join(input_dir, "input.jpg")
    
    if not os.path.exists(input_image_path):
        print(f"请将要处理的图片放在以下目录，并命名为 input.jpg：")
        print(input_dir)
        return

    # 检查框架样式是否有效
    styles = ImageEnhancer.get_supported_styles()
    if frame_style not in styles['frames']:
        print(f"未知的框架样式: {frame_style}")
        print(f"支持的框架样式: {', '.join(styles['frames'])}")
        return

    # 首先生成原色彩效果
    output_path = os.path.join(output_dir, f"{frame_style}.jpg")
    process_image(input_image_path, output_path, frame_style)

    # 如果没有指定色彩风格，则只保留原色彩效果
    if not color_styles:
        return

    # 检查并处理每个色彩风格
    for color_style in color_styles:
        if color_style not in styles['effects']:
            print(f"未知的色彩风格: {color_style}")
            print(f"支持的色彩风格: {', '.join(styles['effects'])}")
            continue
            
        output_name = f"{frame_style}_{color_style}.jpg"
        output_path = os.path.join(output_dir, output_name)
        process_image(input_image_path, output_path, frame_style, color_style)

def generate_all_combinations():
    """生成所有可能的框架和效果组合"""
    styles = ImageEnhancer.get_supported_styles()
    frames = styles['frames']
    effects = styles['effects']
    
    for frame in frames:
        # 生成原始框架效果
        generate_styles(frame)
        
        # 生成每种效果的组合
        for effect in effects:
            generate_styles(frame, [effect])

def generate_random_combinations(count=5):
    """生成指定数量的随机框架和效果组合"""
    import random
    
    styles = ImageEnhancer.get_supported_styles()
    frames = styles['frames']
    effects = styles['effects']
    
    # 确保不重复生成相同的组合
    combinations = set()
    while len(combinations) < count:
        frame = random.choice(frames)
        effect = random.choice(effects)
        combinations.add((frame, effect))
    
    # 生成选中的组合
    for frame, effect in combinations:
        generate_styles(frame, [effect])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='图片风格处理工具')
    parser.add_argument('--frame', '-f', default='polaroid', 
                       choices=['original', 'polaroid', 'symmetric'],
                       help='框架样式')
    parser.add_argument('--effects', '-e', nargs='*',
                       help='色彩效果，可以指定多个')
    parser.add_argument('--random', '-r', type=int, metavar='N',
                       help='生成N个随机组合')
    parser.add_argument('--all', '-a', action='store_true',
                       help='生成所有可能的组合')
    parser.add_argument('--all-effects', '-ae', action='store_true',
                       help='生成指定框架下的所有色彩效果')
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_combinations()
    elif args.random:
        generate_random_combinations(args.random)
    elif args.all_effects:
        # 获取所有支持的色彩效果
        styles = ImageEnhancer.get_supported_styles()
        # 生成指定框架下的所有色彩效果
        generate_styles(args.frame, styles['effects'])
    else:
        generate_styles(args.frame, args.effects)