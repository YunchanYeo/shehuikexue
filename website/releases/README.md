# 可选：下载页用安装包目录

**默认分发不需要本目录。** 直接把 `dist/SpeechEval.dmg` 与 `dist/SpeechEval-Setup.exe` 发给用户即可。

仅在使用 `website/index.html` 下载页时，才把构建产物复制到这里：

| 文件 | 来源 |
|------|------|
| `SpeechEval.dmg` | `dist/SpeechEval.dmg` |
| `SpeechEval-Setup.exe` | `dist/SpeechEval-Setup.exe` |

复制命令（可选）：`./scripts/prepare_release.sh` 或 `scripts\prepare_release.bat`
