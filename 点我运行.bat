@echo off
:: 版权归属于 @Sacilave (https://github.com/Sacilave)
:: 项目原地址: https://github.com/Sacilave/polaroid-style-generator

chcp 65001 > nul
title Polaroid Style Generator

:: 检查 Python 环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo "Python未安装或未添加到环境变量!"
    echo "请安装Python并确保其已添加到环境变量."
    pause
    exit /b 1
)

:: 检查必要文件
if not exist "main.py" (
    echo "未找到main.py文件!"
    echo "请确保在正确的目录下运行此脚本."
    pause
    exit /b 1
)

:: 创建必要的目录
if not exist "images\input" mkdir "images\input"
if not exist "images\output" mkdir "images\output"

:menu
cls
echo "============================================"
echo "         Polaroid Style Generator"
echo "============================================"
echo "     Copyright @Sacilave (github.com/Sacilave)"
echo.
echo "请选择操作方式:"
echo.
echo "[1] 快捷菜单"
echo "[2] 直接输入编号"
echo "[3] 压缩图片"
echo "[0] 退出"
echo.
echo "============================================"

set /p "choice=请输入选项数字: "

if "%choice%"=="1" goto quick_menu
if "%choice%"=="2" goto input_numbers
if "%choice%"=="3" goto compress
if "%choice%"=="0" goto end

echo "无效的选项, 请重试"
timeout /t 2 > nul
goto menu

:quick_menu
cls
echo "============================================"
echo "         Polaroid Style Generator"
echo "============================================"
echo "     Copyright @Sacilave (github.com/Sacilave)"
echo.
echo "请选择操作方式:"
echo.
echo "[1] 拍立得框架 (原色)"
echo "[2] 拍立得框架 + 复古效果"
echo "[3] 拍立得框架 + 经典黑白"
echo "[4] 拍立得框架 + 70年代风格"
echo "[5] 拍立得框架的所有效果"
echo.
echo "[6] 对称边框 (原色)"
echo "[7] 对称边框 + 复古效果"
echo "[8] 对称边框 + 经典黑白"
echo "[9] 对称边框的所有效果"
echo.
echo "[10] 生成5个随机组合"
echo "[11] 生成所有可能的组合"
echo "[12] 进入编号输入模式"
echo "[0] 返回主菜单"
echo.
echo "============================================"

set /p "choice=请输入选项数字: "

if "%choice%"=="0" goto menu
if "%choice%"=="1" (
    echo "生成拍立得框架原色效果..."
    python main.py -f polaroid 2>nul
    goto check_error
)
if "%choice%"=="2" (
    echo "生成拍立得框架 + 复古效果..."
    python main.py -f polaroid -e vintage 2>nul
    goto check_error
)
if "%choice%"=="3" (
    echo "生成拍立得框架 + 经典黑白效果..."
    python main.py -f polaroid -e bw_classic 2>nul
    goto check_error
)
if "%choice%"=="4" (
    echo "生成拍立得框架 + 70年代风格..."
    python main.py -f polaroid -e instant_70s 2>nul
    goto check_error
)
if "%choice%"=="5" (
    echo "生成拍立得框架的所有效果..."
    python main.py -f polaroid -ae 2>nul
    goto check_error
)
if "%choice%"=="6" (
    echo "生成对称边框原色效果..."
    python main.py -f symmetric 2>nul
    goto check_error
)
if "%choice%"=="7" (
    echo "生成对称边框 + 复古效果..."
    python main.py -f symmetric -e vintage 2>nul
    goto check_error
)
if "%choice%"=="8" (
    echo "生成对称边框 + 经典黑白效果..."
    python main.py -f symmetric -e bw_classic 2>nul
    goto check_error
)
if "%choice%"=="9" (
    echo "生成对称边框的所有效果..."
    python main.py -f symmetric -ae 2>nul
    goto check_error
)
if "%choice%"=="10" (
    echo "生成5个随机组合..."
    python main.py -r 5 2>nul
    goto check_error
)
if "%choice%"=="11" (
    echo "生成所有可能的组合..."
    python main.py -a 2>nul
    goto check_error
)
if "%choice%"=="12" goto input_numbers

echo "无效的选项, 请重试"
timeout /t 2 > nul
goto quick_menu

:check_error
if %errorlevel% neq 0 (
    echo "错误: 处理失败"
    echo "请确保:"
    echo "1. images/input/目录中存在input.jpg"
    echo "2. 图片格式正确"
    echo "3. 有足够的磁盘空间"
)
pause
goto quick_menu

:input_numbers
cls
echo "============================================"
echo "框架编号:"
echo "1 - polaroid (拍立得)"
echo "2 - symmetric (对称边框)"
echo "3 - original (原始)"
echo.
echo "色彩效果编号:"
echo " 1 - vintage (复古)         7 - cinematic_kodak (柯达)"
echo " 2 - bw_classic (经典黑白)   8 - cinematic_fuji (富士)"
echo " 3 - bw_high_contrast (高对比) 9 - cinematic_vision3 (Vision3)"
echo " 4 - bw_soft (柔和)         10 - retro_60s (60年代)"
echo " 5 - instant_70s (70年代)    11 - retro_70s (70年代)"
echo " 6 - instant_80s (80年代)    12 - retro_80s (80年代)"
echo.
echo "使用方法:"
echo "1. 输入框架编号生成该框架的所有效果"
echo "2. 输入'框架编号 色彩编号'生成指定组合"
echo "   例如: 1 1 (拍立得框架+复古效果)"
echo "3. 输入'0'返回主菜单"
echo "============================================"

set /p "input=请输入: "

:: 检查是否要返回主菜单
if "%input%"=="0" goto menu

:: 检查输入是否为空
if "%input%"=="" (
    echo "错误: 输入不能为空"
    timeout /t 2 > nul
    goto input_numbers
)

:: 分割输入的数字
for /f "tokens=1,2" %%a in ("%input%") do (
    set "frame=%%a"
    set "effect=%%b"
)

:: 验证框架编号
if not defined frame (
    echo "错误: 无效的输入格式"
    timeout /t 2 > nul
    goto input_numbers
)

:: 检查框架编号范围
if %frame% LSS 1 (
    echo "错误: 框架编号必须在1-3之间"
    timeout /t 2 > nul
    goto input_numbers
)
if %frame% GTR 3 (
    echo "错误: 框架编号必须在1-3之间"
    timeout /t 2 > nul
    goto input_numbers
)

:: 映射框架编号到名称
if "%frame%"=="1" (set "frame_name=polaroid")
if "%frame%"=="2" (set "frame_name=symmetric")
if "%frame%"=="3" (set "frame_name=original")

:: 如果只输入了框架编号
if "%effect%"=="" (
    echo "生成 %frame_name% 框架的所有效果..."
    python main.py -f %frame_name% -ae 2>nul
    if %errorlevel% neq 0 (
        echo "错误: 处理失败"
        echo "请确保:"
        echo "1. images/input/目录中存在input.jpg"
        echo "2. 图片格式正确"
        echo "3. 有足够的磁盘空间"
    )
    pause
    goto input_numbers
)

:: 检查效果编号范围
if %effect% LSS 1 (
    echo "错误: 色彩效果编号必须在1-12之间"
    timeout /t 2 > nul
    goto input_numbers
)
if %effect% GTR 12 (
    echo "错误: 色彩效果编号必须在1-12之间"
    timeout /t 2 > nul
    goto input_numbers
)

:: 映射效果编号到名称
if "%effect%"=="1" (set "effect_name=vintage")
if "%effect%"=="2" (set "effect_name=bw_classic")
if "%effect%"=="3" (set "effect_name=bw_high_contrast")
if "%effect%"=="4" (set "effect_name=bw_soft")
if "%effect%"=="5" (set "effect_name=instant_70s")
if "%effect%"=="6" (set "effect_name=instant_80s")
if "%effect%"=="7" (set "effect_name=cinematic_kodak")
if "%effect%"=="8" (set "effect_name=cinematic_fuji")
if "%effect%"=="9" (set "effect_name=cinematic_vision3")
if "%effect%"=="10" (set "effect_name=retro_60s")
if "%effect%"=="11" (set "effect_name=retro_70s")
if "%effect%"=="12" (set "effect_name=retro_80s")

:: 生成指定组合
echo "生成 %frame_name% 框架 + %effect_name% 效果..."
python main.py -f %frame_name% -e %effect_name% 2>nul
if %errorlevel% neq 0 (
    echo "错误: 处理失败"
    echo "请确保:"
    echo "1. images/input/目录中存在input.jpg"
    echo "2. 图片格式正确"
    echo "3. 有足够的磁盘空间"
)
pause
goto input_numbers

:compress
cls
echo "============================================"
echo "              压缩图片"
echo "============================================"
echo.
echo "[1] 压缩指定目录下的图片"
echo "[2] 压缩output目录下的图片"
echo "[3] 返回主菜单"
echo.
set /p "compress_choice=请选择: "

if "%compress_choice%"=="3" goto menu
if "%compress_choice%"=="2" (
    set "dir=%~dp0images\output"
    goto check_compress_dir
)
if not "%compress_choice%"=="1" (
    echo "无效的选项, 请重试"
    timeout /t 2 > nul
    goto compress
)

:: 获取目录路径
set /p "dir=请输入要压缩的图片目录路径: "

:check_compress_dir
:: 检查目录路径是否为空
if "%dir%"=="" (
    echo "错误: 目录路径不能为空"
    timeout /t 2 > nul
    goto compress
)

:: 检查目录是否存在
if not exist "%dir%" (
    echo "错误: 目录不存在: %dir%"
    echo "请检查路径是否正确"
    timeout /t 2 > nul
    goto compress
)

:: 检查目录中是否有图片文件
set "found_images=0"
for %%f in ("%dir%\*.jpg", "%dir%\*.jpeg", "%dir%\*.png") do (
    set "found_images=1"
)

if "%found_images%"=="0" (
    echo "错误: 指定目录中未找到任何图片文件"
    echo "支持的格式: jpg, jpeg, png"
    timeout /t 2 > nul
    goto compress
)

:: 获取压缩质量
set /p "quality=请输入压缩质量(1-100, 默认70): "
if "%quality%"=="" set quality=70

:: 验证压缩质量范围
if %quality% LSS 1 (
    echo "错误: 压缩质量必须在1-100之间"
    timeout /t 2 > nul
    goto compress
)
if %quality% GTR 100 (
    echo "错误: 压缩质量必须在1-100之间"
    timeout /t 2 > nul
    goto compress
)

:: 执行压缩
echo.
echo "开始压缩图片..."
echo "目标目录: %dir%"
python main.py -c "%dir%" -q %quality% 2>nul

if %errorlevel% neq 0 (
    echo "错误: 压缩过程中出现错误"
    echo "请确保:"
    echo "1. 有足够的磁盘空间"
    echo "2. 对目录有写入权限"
    echo "3. 图片文件未被其他程序占用"
    timeout /t 2 > nul
)

pause
goto compress

:menu_old
:: 原来的菜单内容...

:end
echo "感谢使用!"
timeout /t 2 > nul
exit /b 0 