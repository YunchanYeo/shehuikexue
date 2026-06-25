# 中文口语评估 

本地程序：对**人声**音频计算流利度、丰富性、生动性，**不调用云端大模型 API**，**无需服务器**。  
提供 **桌面应用**（推荐给不会用终端的用户）和命令行两种方式。

---

## 桌面应用（推荐）

### 最终用户：Mac 安装包

收到 **`SpeechEval.dmg`** 后：双击 → 拖入「应用程序」→ 打开。  
若无法打开：**右键 → 打开**。

**使用步骤（中文界面）：**

1. 点击 **「选择文件」**，选择录音（wav、mp3、m4a 等）。
2. 保持 **「降噪处理」** 开启（默认），可减弱背景杂音后再评估。
3. 点击 **「开始评估」**（首次运行会下载语音识别模型，需联网）。
4. 窗口下方查看 **流利度、丰富性、生动性、总分**。
5. 可选：**保存 JSON**、**复制结果**。

> 全部在本机 CPU/GPU 上运行，不上传音频到云端服务器。

### 开发者：本地运行 GUI（未打包）

```bash
# macOS / Linux
chmod +x scripts/run_app.sh
./scripts/run_app.sh

# Windows
scripts\run_app.bat
```

或：`pip install -r requirements.txt` 后执行 `python app_gui.py`。

### 制作 Mac 安装包（本地，不用 GitHub）

**双击** 项目里的 **`制作安装包.command`**，等待约 10–20 分钟，**桌面会出现 `SpeechEval.dmg`**。

或终端：

```bash
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh
```

详见 **[docs/Mac-安装包.md](docs/Mac-安装包.md)**。建议 Python **3.10–3.12**（3.14 可能失败）。

---

## 命令行（可选）

### 安装

```bash
cd /Users/yeoyunchan/Desktop/shehuikexue
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

首次运行会下载 Whisper 权重（默认 `base`）。

## 使用

```bash
python evaluate.py your_speech.wav
python evaluate.py your_speech.wav --json
python evaluate.py your_speech.wav --transcript "你好，我认为这个问题很重要。"
python evaluate.py your_speech.wav --whisper-model small --device cuda
```

**Z 分常模（必知）**：Z = (值 − 总体均值) / 总体标准差，需要**多条录音**先标定，不能对单条音频在当次样本内算（N=1 时标准差为 0）。

```bash
# 下面路径是示例，请改成你电脑上真实的文件夹/文件（不要照抄占位符）
python calibrate_norms.py ~/Desktop/我的口语录音文件夹
python evaluate.py ~/Desktop/我的口语录音文件夹/学生01.wav
```

标定要求：文件夹里至少 **2 个** wav/mp3/m4a 等文件。

也可手动编辑 `speech_eval/norms.yaml` 中的 `mean` / `std`。

---

## 计分公式

| 维度 | 公式 |
|------|------|
| **流利度** | \(\frac{1}{4}(Z_{\text{发音速率}} - Z_{\text{无声停顿}} - Z_{\text{填充词}} - Z_{\text{重复修正}})\) |
| **丰富性** | \(\frac{1}{3}(Z_{\text{TTR}} + Z_{\text{平均句长}} + Z_{\text{连接词}})\) |
| **生动性** | \(\frac{1}{2}(Z_{\text{基频SD}} + Z_{\text{强度SD}})\) |
| **总分** | 三维度的算术平均 |

---

## 指标说明（中文）

| 指标 | 计算方法 | 含义 |
|------|----------|------|
| **发音速率** | 去掉长无声段后的“说话时长”内，每秒音节数（汉字数近似音节） | 组织语言的速度；越高越利索 |
| **无声停顿占比** | 能量低于阈值且 **>0.2s** 的无声段时长 / 总时长 | 思考性停顿；越高越卡顿 |
| **基频标准差** | 全段 F0（librosa YIN）在浊音帧上的标准差 | 语调起伏；越大越生动 |
| **强度标准差** | 短时 RMS 能量的标准差 | 音量起伏；配合音高体现感染力 |
| **填充词密度** | “嗯、啊、就是、那个…” 等出现次数 / 总词数 | 口语不流利的重要信号 |
| **重复/修正密度** | 正则检测“我我…”、相邻重复词、简单自我修正 / 总词数 | 计划失调、组织困难 |
| **词汇多样性 (TTR)** | 不重复词数 / 总词数（jieba 分词） | 词汇量；受篇幅影响大 |
| **平均句长** | 按。！？；分句后的平均词数 | 句子是否完整；过低可能碎片化 |
| **连接词密度** | 预设连接词表命中数 / 总词数 | 条理与逻辑衔接 |

---