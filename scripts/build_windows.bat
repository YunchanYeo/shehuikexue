@echo off
REM Build Windows: SpeechEval.exe + SpeechEval-Setup.exe (installer)
cd /d "%~dp0\.."

echo Python version:
python --version

python -m venv .venv-build
call .venv-build\Scripts\activate.bat
python -m pip install -U pip wheel
pip install -r requirements.txt
pip install pyinstaller

echo.
echo ^>^>^> PyInstaller 打包 ...
pyinstaller speech_eval.spec --noconfirm --clean

if not exist "dist\SpeechEval\SpeechEval.exe" (
  echo 错误：未找到 dist\SpeechEval\SpeechEval.exe
  pause
  exit /b 1
)

set ISCC=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
  set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
  set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if defined ISCC (
  echo.
  echo ^>^>^> Inno Setup 制作安装程序 ...
  "%ISCC%" installer\windows.iss
) else (
  echo.
  echo [警告] 未安装 Inno Setup 6，无法生成 SpeechEval-Setup.exe
  echo 请下载安装: https://jrsoftware.org/isdl.php
  echo 安装后重新运行本脚本。
  pause
  exit /b 1
)

if not exist "dist\SpeechEval-Setup.exe" (
  echo 错误：未生成 dist\SpeechEval-Setup.exe
  pause
  exit /b 1
)

echo.
echo ==========================================
echo  完成
echo   - 安装程序: dist\SpeechEval-Setup.exe  ^(发给用户^)
echo ==========================================
echo.
echo 分发: 将 dist\SpeechEval-Setup.exe 发给用户（网盘 / 邮件 / GitHub Releases 等）
echo 用户: 双击安装程序，按向导完成安装

pause
