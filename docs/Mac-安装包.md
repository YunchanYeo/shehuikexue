# Mac 安装包（DMG）— 本地制作，不用 GitHub

## 方法一：双击（最简单）

1. 在 Finder 中打开项目文件夹 `kouyu`（克隆后的目录名）
2. **双击** `制作安装包.command`
3. 若提示「无法打开」：**右键 → 打开** → 确认
4. 等待约 **10–20 分钟**（窗口会显示进度）
5. 完成后 **桌面上会出现 `SpeechEval.dmg`**

## 方法二：终端

```bash
git clone https://github.com/YunchanYeo/kouyu.git
cd kouyu
./scripts/build_mac.sh
```

完成后：

- `dist/SpeechEval.dmg`
- **`~/Desktop/SpeechEval.dmg`**（已自动复制到桌面）

## 分发给用户

把 **`SpeechEval.dmg`** 用网盘、微信、邮件等发给对方即可。

用户安装：双击 dmg → 将 **SpeechEval** 拖入 **应用程序**。

## 仅测试应用（不打包）

```bash
./scripts/run_app.sh
```

## 要求

- macOS（Apple 芯片或 Intel 均可）
- Python 3.10 或更高（建议 3.11/3.12）
- 联网（首次打包需下载依赖）

若打包失败，可安装 Python 3.12：https://www.python.org/downloads/
