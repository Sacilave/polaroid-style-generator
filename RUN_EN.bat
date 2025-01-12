@echo off
:: Copyright belongs to @Sacilave (https://github.com/Sacilave)
:: Project URL: https://github.com/Sacilave/polaroid-style-generator

chcp 65001 > nul
title Polaroid Style Generator

:: Check Python environment
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo "Python is not installed or not in PATH!"
    echo "Please install Python and ensure it's added to PATH."
    pause
    exit /b 1
)

:: Check required files
if not exist "main.py" (
    echo "main.py not found!"
    echo "Please ensure you're running this script in the correct directory."
    pause
    exit /b 1
)

:: Create necessary directories
if not exist "images\input" mkdir "images\input"
if not exist "images\output" mkdir "images\output"

:menu
cls
echo "============================================"
echo "         Polaroid Style Generator"
echo "============================================"
echo "     Copyright @Sacilave (github.com/Sacilave)"
echo.
echo "Select operation mode:"
echo.
echo "[1] Quick Menu"
echo "[2] Enter Style Numbers"
echo "[3] Compress Images"
echo "[0] Exit"
echo.
echo "============================================"

set /p "choice=Enter your choice: "

if "%choice%"=="1" goto quick_menu
if "%choice%"=="2" goto input_numbers
if "%choice%"=="3" goto compress
if "%choice%"=="0" goto end

echo "Invalid option, please try again"
timeout /t 2 > nul
goto menu

:quick_menu
cls
echo "============================================"
echo "         Polaroid Style Generator"
echo "============================================"
echo "     Copyright @Sacilave (github.com/Sacilave)"
echo.
echo "[1] Polaroid Frame (Original)"
echo "[2] Polaroid Frame + Vintage"
echo "[3] Polaroid Frame + Classic B&W"
echo "[4] Polaroid Frame + 70s Style"
echo "[5] All Effects with Polaroid Frame"
echo.
echo "[6] Symmetric Frame (Original)"
echo "[7] Symmetric Frame + Vintage"
echo "[8] Symmetric Frame + Classic B&W"
echo "[9] All Effects with Symmetric Frame"
echo.
echo "[10] Generate 5 Random Combinations"
echo "[11] Generate All Possible Combinations"
echo "[12] Enter Number Input Mode"
echo "[0] Back to Main Menu"
echo.
echo "============================================"

set /p "choice=Enter your choice: "

if "%choice%"=="0" goto menu
if "%choice%"=="1" (
    echo "Generating Polaroid frame original effect..."
    python main.py -f polaroid 2>nul
    goto check_error
)
:: ... (其他选项保持相同的 Python 命令，只改变提示文本)

:check_error
if %errorlevel% neq 0 (
    echo "Error: Processing failed"
    echo "Please ensure:"
    echo "1. input.jpg exists in images/input/ directory"
    echo "2. Image format is correct"
    echo "3. Sufficient disk space available"
)
pause
goto quick_menu

:input_numbers
cls
echo "============================================"
echo "Frame Numbers:"
echo "1 - polaroid (Polaroid style)"
echo "2 - symmetric (Symmetric border)"
echo "3 - original (No frame)"
echo.
echo "Color Effect Numbers:"
echo " 1 - vintage              7 - cinematic_kodak"
echo " 2 - bw_classic          8 - cinematic_fuji"
echo " 3 - bw_high_contrast    9 - cinematic_vision3"
echo " 4 - bw_soft            10 - retro_60s"
echo " 5 - instant_70s        11 - retro_70s"
echo " 6 - instant_80s        12 - retro_80s"
echo.
echo "Instructions:"
echo "1. Enter frame number to generate all effects"
echo "2. Enter 'frame_number effect_number' for specific combination"
echo "   Example: 1 1 (Polaroid frame + Vintage effect)"
echo "3. Enter '0' to return to main menu"
echo "============================================"

:: ... (其余逻辑保持不变，只改变错误提示文本)

:compress
cls
echo "============================================"
echo "           Compress Images"
echo "============================================"
echo.
echo "[1] Compress Images in Specified Directory"
echo "[2] Compress Images in Output Directory"
echo "[3] Back to Main Menu"
echo.
set /p "compress_choice=Enter your choice: "

if "%compress_choice%"=="3" goto menu
if "%compress_choice%"=="2" (
    set "dir=%~dp0images\output"
    goto check_compress_dir
)
if not "%compress_choice%"=="1" (
    echo "Invalid option, please try again"
    timeout /t 2 > nul
    goto compress
)

:: Get directory path
set /p "dir=Enter directory path: "

:check_compress_dir
:: Check if directory path is empty
if "%dir%"=="" (
    echo "Error: Directory path cannot be empty"
    timeout /t 2 > nul
    goto compress
)

:: Check if directory exists
if not exist "%dir%" (
    echo "Error: Directory does not exist: %dir%"
    echo "Please check the path"
    timeout /t 2 > nul
    goto compress
)

:: Check for image files
set "found_images=0"
for %%f in ("%dir%\*.jpg", "%dir%\*.jpeg", "%dir%\*.png") do (
    set "found_images=1"
)

if "%found_images%"=="0" (
    echo "Error: No image files found in specified directory"
    echo "Supported formats: jpg, jpeg, png"
    timeout /t 2 > nul
    goto compress
)

:: Get compression quality
set /p "quality=Enter compression quality (1-100, default 70): "
if "%quality%"=="" set quality=70

:: Validate quality range
if %quality% LSS 1 (
    echo "Error: Quality must be between 1-100"
    timeout /t 2 > nul
    goto compress
)
if %quality% GTR 100 (
    echo "Error: Quality must be between 1-100"
    timeout /t 2 > nul
    goto compress
)

:: Execute compression
echo.
echo "Starting image compression..."
echo "Target directory: %dir%"
python main.py -c "%dir%" -q %quality% 2>nul

if %errorlevel% neq 0 (
    echo "Error: Compression failed"
    echo "Please ensure:"
    echo "1. Sufficient disk space"
    echo "2. Write permission to directory"
    echo "3. Images are not in use by other programs"
    timeout /t 2 > nul
)

pause
goto compress

:end
echo "Thanks for using!"
timeout /t 2 > nul
exit /b 0 