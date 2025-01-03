# Polaroid Style Generator

一个处理图片的工具，给图片添加拍立得边框（或等距边框和无边框），以及多种复古和艺术效果风格

## 目录
> 使用者直接看 [命令行使用](#命令行使用)
- [安装说明](#安装说明)
- [项目结构](#项目结构)
- [功能特性](#功能特性)
  - [框架样式](#框架样式)
  - [色彩效果](#色彩效果)
    1. 复古效果
    2. 黑白胶片
    3. 即时显影
    4. 交叉冲洗
    5. 电影胶片
    6. 复古彩色
  - [处理特点](#处理特点)
- [使用方法](#使用方法)
- [技术实现](#技术实现)
  - [核心类](#核心类)
  - [扩展性设计](#扩展性设计)
- [维护说明](#维护说明)
  - [添加新框架](#添加新框架)
  - [添加新色彩效果](#添加新色彩效果)
  - [代码规范](#代码规范)
- [贡献指南](#贡献指南)
- [命令行使用](#命令行使用)
- [License](#license)

## 安装说明

### 1. 下载项目
```bash
# 克隆项目
git clone https://github.com/your-username/polaroid-style-generator.git

# 进入项目目录
cd polaroid-style-generator
```

### 2. 环境要求
- Python 3.6 或更高版本
- pip (Python包管理器)

### 3. 安装依赖
```bash
# 使用 pip 安装所需的包
pip install -r requirements.txt

# 或者直接安装必需的包
pip install Pillow==10.0.0
pip install numpy==1.24.3
```

### 4. 创建必要的目录
```bash
# 创建输入输出目录
mkdir -p images/input images/output
```

### 5. 准备图片
- 将要处理的图片重命名为 `input.jpg`
- 将图片放入 `images/input/` 目录

### 6. 运行程序
```bash
# 基本使用（使用拍立得框架）
python main.py -f polaroid

# 查看帮助
python main.py --help
```

## 项目结构

```
GalleryPicProcessor/
├── main.py              # 主程序入口
├── image_enhancer.py    # 图片处理核心类
└── images/              # 图片目录
    ├── input/           # 输入图片目录
    └── output/          # 输出图片目录
```

## 功能特性

### 框架样式
- `original`: 无框架，保持原始尺寸
- `polaroid`: 经典拍立得框架（底部加宽）
- `symmetric`: 对称边框（四边等宽）

### 色彩效果
1. **复古效果**
   - `vintage`: 经典复古褪色效果

2. **黑白胶片**
   - `bw_classic`: 经典黑白效果
   - `bw_high_contrast`: 高对比度黑白
   - `bw_soft`: 柔和黑白

3. **即时显影**
   - `instant_70s`: 70年代风格（偏绿）
   - `instant_80s`: 80年代风格（偏暖）
   - `instant_90s`: 90年代风格（自然）

4. **交叉冲洗**
   - `cross_process`: 标准交叉冲洗
   - `cross_light`: 轻度交叉冲洗
   - `cross_strong`: 强烈交叉冲洗

5. **电影胶片**
   - `cinematic_kodak`: 柯达风格（暖色调）
   - `cinematic_fuji`: 富士风格（清爽）
   - `cinematic_vision3`: Vision3风格（自然）

6. **复古彩色**
   - `retro_60s`: 60年代风格（高饱和）
   - `retro_70s`: 70年代风格（偏黄）
   - `retro_80s`: 80年代风格（偏红）

### 处理特点
- 框架和色彩效果可自由组合
- 保持原图分辨率不变
- 高质量图片输出
- 细腻的颗粒感效果
- 独特的色彩处理

## 使用方法

1. 准备工作
   - 确保已安装 Python 3.x
   - 安装依赖: `pip install Pillow numpy`

2. 放置图片
   - 将要处理的图片命名为 `input.jpg`
   - 放入 `images/input/` 目录

3. 运行程序
   ```python
   # 1. 只应用框架
   generate_styles('polaroid')  # 生成原色拍立得效果
   
   # 2. 框架 + 单个色彩效果
   generate_styles('symmetric', ['vintage'])  # 生成复古对称框架效果
   
   # 3. 框架 + 多个色彩效果
   generate_styles('polaroid', [
       'vintage',
       'bw_classic',
       'instant_70s',
       'cinematic_kodak'
   ])
   ```

4. 查看结果
   - 处理后的图片将保存在 `images/output/` 目录
   - 输出文件名格式：`框架_色彩.jpg`
   - 例如：`polaroid_vintage.jpg`

## 技术实现

### 核心类
- `StyleProcessor`: 样式处理器基类
- `PolaroidStyle`: 拍立得框架实现
- `SymmetricPolaroidStyle`: 对称框架实现
- `BWFilmStyle`: 黑白胶片效果
- `InstantStyle`: 即时显影效果
- `CrossProcessStyle`: 交叉冲洗效果
- `CinematicStyle`: 电影胶片效果
- `RetroColorStyle`: 复古彩色效果
- `ImageEnhancer`: 图片增强器主类

### 扩展性设计
- 采用抽象基类设计
- 框架和色彩效果分离
- 支持轻松添加新的处理器
- 灵活的参数配置系统

## 维护说明

### 添加新框架
1. 在 `image_enhancer.py` 中创建新的框架处理器类
2. 继承 `StyleProcessor` 基类
3. 实现 `process` 方法
4. 在 `ImageEnhancer.frame_processors` 中注册

### 添加新色彩效果
1. 在 `image_enhancer.py` 中创建新的色彩处理器类
2. 继承 `StyleProcessor` 基类
3. 实现 `process` 方法
4. 在 `ImageEnhancer.color_processors` 中注册

### 代码规范
- 遵循 PEP 8 编码规范
- 保持类和方法的单一职责
- 添加适当的注释和文档字符串
- 使用类型提示增强代码可读性

## 贡献指南

欢迎提交 Pull Request 或 Issue，建议遵循以下原则：
- 保持代码风格一致
- 添加必要的测试
- 更新相关文档
- 提供效果示例

## 命令行使用

#### 基础使用
```bash
python main.py -f [frame] -e [effect]  
```
    参数说明：
    frame: polaroid（拍立得）, symmetric（对称边框）, original（原始）; 
    effect: vintage（复古）, 
        bw_classic（经典黑白）, 
        instant_70s（70年代即时）, 
        cinematic_kodak（电影胶片柯达）, 
        cinematic_fuji（电影胶片富士）, 
        cinematic_vision3（电影胶片Vision3）, 
        retro_60s（60年代复古）, 
        retro_70s（70年代复古）, 
        retro_80s（80年代复古）, 
        cross_process（交叉处理）, 
        cross_light（轻度交叉处理）, 
        cross_strong（强烈交叉处理）

#### 使用拍立得框架生成原始效果
```bash
python main.py -f polaroid
```

#### 生成拍立得框架下的指定效果组合
```bash
python main.py -f polaroid -e vintage bw_classic instant_70s
```

#### 生成拍立得框架下的所有色彩效果
```bash
python main.py -f polaroid -ae
```

#### 生成5个随机组合
```bash
python main.py -r 5
```

#### 生成所有可能的组合
```bash
python main.py -a
```

## License
This project is proprietary software.
All rights reserved. See [LICENSE](LICENSE) for details.
Unauthorized copying, modification, distribution, or use is strictly prohibited.