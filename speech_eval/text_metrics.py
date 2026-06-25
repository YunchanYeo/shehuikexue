"""Text-based metrics from transcript (Chinese)."""

from __future__ import annotations

import re

import jieba


# Filled pauses / discourse fillers (口语填充词)
FILLERS = [
    "嗯",
    "啊",
    "呃",
    "额",
    "噢",
    "哦",
    "哎",
    "诶",
    "就是",
    "那个",
    "这个",
    "怎么说呢",
    "怎么说",
    "反正",
    "其实",
    "基本上",
    "好像",
    "对吧",
    "是吧",
]

# Connectives (连接词)
CONNECTIVES = [
    "因为",
    "所以",
    "虽然",
    "但是",
    "然而",
    "而且",
    "并且",
    "或者",
    "如果",
    "那么",
    "因此",
    "于是",
    "然后",
    "接着",
    "首先",
    "其次",
    "再次",
    "最后",
    "总之",
    "例如",
    "比如",
    "不过",
    "何况",
    "除非",
    "无论",
    "尽管",
    "以便",
    "为了",
]

# Oral ASR often omits 。；treat clause breaks as utterance boundaries too.
SENTENCE_END = re.compile(r"[。！？；\n，、]+")


def count_syllables_chinese(text: str) -> int:
    """Approximate syllable count: one per Chinese character."""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def tokenize(text: str) -> list[str]:
    text = re.sub(r"\s+", "", text)
    if not text:
        return []
    return [w for w in jieba.lcut(text) if w.strip()]


def filled_pause_density(text: str) -> float:
    tokens = tokenize(text)
    n = len(tokens)
    if n == 0:
        return 0.0
    count = sum(1 for tok in tokens if tok in FILLERS)
    compact = re.sub(r"\s+", "", text)
    for filler in sorted(FILLERS, key=len, reverse=True):
        if len(filler) >= 2:
            count += compact.count(filler)
    return min(1.0, count / n)


def repetition_repair_density(text: str) -> float:
    """
    Detect immediate repetitions and simple self-repairs.
    Examples: 我我, 去去, 我们...呃，去
    """
    tokens = tokenize(text)
    n = len(tokens)
    if n == 0:
        return 0.0

    repairs = 0
    # Character-level stutter within tokens
    for tok in tokens:
        if re.search(r"(.)\1{1,}", tok):
            repairs += 1
    # Adjacent duplicate tokens
    for i in range(1, len(tokens)):
        if tokens[i] == tokens[i - 1]:
            repairs += 1
    # Truncation + restart: X...Y where short fragment repeats start
    raw = re.sub(r"\s+", "", text)
    if re.search(r"([\u4e00-\u9fff]{1,3})[，,、\s]*[呃嗯啊]+[，,、\s]*\1", raw):
        repairs += 1

    return min(1.0, repairs / n)


def type_token_ratio(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def mean_utterance_length(text: str) -> float:
    parts = [p.strip() for p in SENTENCE_END.split(text) if p.strip()]
    if not parts:
        tokens = tokenize(text)
        return float(len(tokens)) if tokens else 0.0
    lengths = [len(tokenize(p)) for p in parts]
    return float(sum(lengths) / len(lengths))


def connective_density(text: str) -> float:
    tokens = tokenize(text)
    n = len(tokens)
    if n == 0:
        return 0.0
    count = sum(1 for t in tokens if t in CONNECTIVES)
    joined = "".join(tokens)
    for phrase in ("因为所以", "虽然但是", "首先其次"):
        count += joined.count(phrase)
    return min(1.0, count / n)


def extract_text_metrics(text: str) -> dict[str, float]:
    return {
        "syllable_count": float(count_syllables_chinese(text)),
        "filled_pause_density": filled_pause_density(text),
        "repetition_repair_density": repetition_repair_density(text),
        "type_token_ratio": type_token_ratio(text),
        "mean_utterance_length": mean_utterance_length(text),
        "connective_density": connective_density(text),
    }
