from PIL import Image
import os

def compress_images(input_dir, quality=70):
    """压缩指定目录中的所有图片
    
    Args:
        input_dir (str): 输入目录路径
        quality (int): 压缩质量，范围1-100，默认70
    """
    if not os.path.exists(input_dir):
        print(f"目录不存在: {input_dir}")
        return
    
    # 获取所有图片文件
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    for filename in image_files:
        input_path = os.path.join(input_dir, filename)
        
        # 打开图片
        with Image.open(input_path) as img:
            # 如果是PNG，先转换为RGB
            if img.format == 'PNG':
                img = img.convert('RGB')
            
            # 压缩并保存
            print(f"正在压缩: {filename}")
            img.save(input_path, 'JPEG', quality=quality, optimize=True)
    
    print("压缩完成！")

if __name__ == "__main__":
    dir = ""  # 要压缩的图片目录
    compress_images(dir)