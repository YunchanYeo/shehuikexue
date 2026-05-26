@echo off
cd /d "%~dp0\.."
set DEST=website\releases
if not exist "%DEST%" mkdir "%DEST%"

if exist "dist\SpeechEval-Setup.exe" (
  copy /Y "dist\SpeechEval-Setup.exe" "%DEST%\"
  echo 已复制: %DEST%\SpeechEval-Setup.exe
) else (
  echo 跳过: dist\SpeechEval-Setup.exe 不存在
)

if exist "dist\SpeechEval.dmg" (
  copy /Y "dist\SpeechEval.dmg" "%DEST%\"
  echo 已复制: %DEST%\SpeechEval.dmg
) else (
  echo 跳过: dist\SpeechEval.dmg 不存在
)

echo.
echo 下载页: 打开 website\index.html 或部署 website 文件夹
