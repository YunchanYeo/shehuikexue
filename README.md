# 中文口语评估 / 중국어 구어 평가

本地程序：对**人声**音频计算流利度、丰富性、生动性，**不调用云端大模型 API**，**无需服务器**。  
提供 **桌面应用**（推荐给不会用终端的用户）和命令行两种方式。

---

## 桌面应用（推荐）/ 데스크톱 앱 (권장)

### 最终用户：安装包（无需网站、无需服务器）

收到安装文件后：

| 系统 | 文件 | 安装 |
|------|------|------|
| **macOS** | `SpeechEval.dmg` | 双击 → 拖入「应用程序」 |
| **Windows** | `SpeechEval-Setup.exe` | 双击 → 按安装向导完成 |

若无法打开 Mac 应用：**右键 → 打开**。Windows SmartScreen：**更多信息 → 仍要运行**。

**使用步骤（中文界面）：**

1. 点击 **「选择文件」**，选择录音（wav、mp3、m4a 等）。
2. 点击 **「开始评估」**（首次运行会下载语音识别模型，需联网）。
3. 窗口下方查看 **流利度、丰富性、生动性、总分**。
4. 可选：**保存 JSON**、**复制结果**。

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

### 开发者：打包成 dmg / exe 安装包

**只有 Mac？** 用 **[GitHub Actions](docs/GitHub-Actions-빌드.md)** 在云端同时打出 dmg 与 Windows 安装包。  
仓库：`https://github.com/YunchanYeo/shehuikexue`（创建与 push 见 [docs/GitHub-저장소-만들기.md](docs/GitHub-저장소-만들기.md)）。

本地打包见 **[docs/打包分发.md](docs/打包分发.md)**（Mac 本地 dmg；Windows 需 Windows 电脑或 Actions）。

```bash
# macOS → 生成 dist/SpeechEval.dmg
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh

# Windows（CMD）→ 生成 dist\SpeechEval-Setup.exe
scripts\build_windows.bat
```

| 平台 | 发给用户的文件 |
|------|----------------|
| Mac | `dist/SpeechEval.dmg` |
| Windows | `dist/SpeechEval-Setup.exe`（需 [Inno Setup](https://jrsoftware.org/isdl.php)） |

用网盘、邮件、U 盘或 GitHub Releases 发送即可。详见 **[docs/打包分发.md](docs/打包分发.md)**。

建议 Python **3.10–3.12**。打包体积约 1–3 GB，首次评估仍会下载 Whisper 模型（需联网一次）。

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

校准常模：编辑 `speech_eval/norms.yaml` 中各指标的 `mean` / `std`（用于 Z 分数）。

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

## 요구사항 및 지표 설명（한국어）

### 종합 점수

| 차원 | 공식 |
|------|------|
| **유창성(流利度)** | \(\frac{1}{4}(Z_{\text{발음 속도}} - Z_{\text{무성 휴지}} - Z_{\text{충전어}} - Z_{\text{반복·수정}})\) |
| **풍부성(丰富性)** | \(\frac{1}{3}(Z_{\text{어휘 다양성}} + Z_{\text{평균 문장 길이}} + Z_{\text{접속어}})\) |
| **생동성(生动性)** | \(\frac{1}{2}(Z_{\text{기본주파수 SD}} + Z_{\text{강도 SD}})\) |
| **총점** | 위 세 차원의 산술 평균 |

※ 무성 휴지·충전어·반복/수정은 **빼기** → 상대적으로 나쁠수록 Z가 커지면 유창성 점수가 낮아짐.

### 각 지표

| 지표 | 계산 요약 | 해석 |
|------|-----------|------|
| **발음 속도 (Articulation Rate)** | 긴 무성 구간을 제외한 말하는 구간만 두고, 초당 음절 수(한자 수로 근사) | 말을 조직하는 속도. 높을수록 말이 빠르고 끊김이 적음 |
| **무성 휴지 비율 (Silent Pause Ratio)** | 0.2초보다 긴 무성 구간 합 / 전체 길이 | 생각하며 멈추는 비율. 높을수록 망설임·끊김 |
| **기본주파수 표준편차 (Pitch F0 SD)** | 성대 진동 주파수(피치) 변화의 표준편차 | 억양의 기복. 클수록 감정·생동감 |
| **강도 표준편차 (Intensity SD)** | 음량(RMS) 변화의 표준편차 | 크고 작은 소리 변화; 표현 몰입도 |
| **충전어 밀도 (Filled Pauses)** | “嗯、啊、就是、那个…” 등 / 전체 단어 수 | 말하며 채우는 습관; 유창성 저하 신호 |
| **반복·수정 밀도 (Repetition & Repair)** | “我我…”, 인접 중복, 간단한 자기 수정 / 단어 수 | 말 계획 실패; 높을수록 조직 어려움 |
| **어휘 다양성 TTR** | 서로 다른 단어 수 / 전체 단어 수 | 어휘 폭; **발화 길이에 민감** |
| **평균 발화 길이** | 。！？ 등으로 나눈 문장당 평균 단어 수 | 문장 완결성; 너무 짧으면 단편적 |
| **접속어 밀도** | “因为、所以、虽然、然后…” 등 / 단어 수 | 논리·담화 구조; 높을수록 체계적 |

### 기술 메모

- **Z 점수**: `speech_eval/norms.yaml`의 모집단 평균·표준편차로 정규화. 실제 비교 전에 자체 코퍼스로 보정 권장.
- **ASR**: 텍스트 지표용 로컬 Whisper. `--transcript`로 수동 입력 가능.
- **클라우드 LLM API**: 사용하지 않음.

---

## 项目结构

```
app_gui.py            # 桌面应用入口
evaluate.py           # 命令行入口
speech_eval.spec      # PyInstaller 打包配置
scripts/
  run_app.sh          # 开发时启动 GUI (Mac/Linux)
  run_app.bat         # 开发时启动 GUI (Windows)
  build_mac.sh        # 打包 macOS .app
  build_windows.bat   # 打包 Windows .exe
website/              # 可选：下载页（不用可忽略）
installer/
  windows.iss         # Windows 安装向导 (Inno Setup)
speech_eval/
  audio_metrics.py    # 声学指标
  text_metrics.py     # 文本指标
  asr.py              # 本地转写
  scoring.py          # Z 分与维度分
  norms.yaml          # 常模参数
```
