"""Human-readable report from evaluation result."""

from __future__ import annotations

from typing import Any


def format_result(result: dict[str, Any], *, lang: str = "zh") -> str:
    m = result["raw_metrics"]
    s = result["scores"]
    transcript = result.get("transcript") or ""

    if lang == "zh":
        lines = [
            f"文件: {result['audio_path']}",
            f"转写: {transcript or '(空)'}",
            "",
            "—— 原始指标 ——",
            f"  发音速率 (音节/秒):     {m['articulation_rate']:.3f}",
            f"  无声停顿占比:           {m['silent_pause_ratio']:.3f}",
            f"  填充词密度:             {m['filled_pause_density']:.3f}",
            f"  重复/修正密度:          {m['repetition_repair_density']:.3f}",
            f"  词汇多样性 (TTR):       {m['type_token_ratio']:.3f}",
            f"  平均句长 (词/句):       {m['mean_utterance_length']:.3f}",
            f"  连接词密度:             {m['connective_density']:.3f}",
            f"  基频标准差 (Hz):        {m['pitch_sd']:.3f}",
            f"  强度标准差:             {m['intensity_sd']:.4f}",
            f"  时长 (秒):              {m['duration_sec']:.2f}",
            "",
            "—— 维度得分 (Z 标准化) ——",
            f"  流利度:   {s['fluency']:.3f}",
            f"  丰富性:   {s['richness']:.3f}",
            f"  生动性:   {s['vividness']:.3f}",
            f"  总分:     {s['total']:.3f}",
        ]
        return "\n".join(lines)

    lines = [
        f"파일: {result['audio_path']}",
        f"전사(중국어): {transcript or '(없음)'}",
        "",
        "—— 원시 지표 ——",
        f"  발음 속도 (음절/초):      {m['articulation_rate']:.3f}",
        f"  무성 휴지 비율:           {m['silent_pause_ratio']:.3f}",
        f"  충전어 밀도:              {m['filled_pause_density']:.3f}",
        f"  반복/수정 밀도:           {m['repetition_repair_density']:.3f}",
        f"  어휘 다양성 (TTR):        {m['type_token_ratio']:.3f}",
        f"  평균 문장 길이 (단어/문): {m['mean_utterance_length']:.3f}",
        f"  접속어 밀도:              {m['connective_density']:.3f}",
        f"  기본주파수 SD (Hz):       {m['pitch_sd']:.3f}",
        f"  강도 SD:                  {m['intensity_sd']:.4f}",
        f"  길이 (초):                {m['duration_sec']:.2f}",
        "",
        "—— 차원 점수 (Z 표준화) ——",
        f"  유창성:   {s['fluency']:.3f}",
        f"  풍부성:   {s['richness']:.3f}",
        f"  생동성:   {s['vividness']:.3f}",
        f"  총점:     {s['total']:.3f}",
    ]
    return "\n".join(lines)
