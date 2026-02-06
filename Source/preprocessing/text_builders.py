"""
- 텍스트 조립 함수
- 스키마 변경시 수정 필요
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
from typing import Dict, List, Tuple, Any
from .text_utils import clean, cap_chars, split_sents_kr, force_1to2_sentences_kr


def build_diag_text(step1: Dict[str, Any]) -> str:
    step1 = step1 or {}
    o = (step1.get("output", {}) or {})
    a = (step1.get("analysis", {}) or {})
    return clean(o.get("summary", "") or a.get("diagnosis_summary", ""))


def extract_diag_core_sentence(diag_text: str) -> str:
    sents = split_sents_kr(diag_text)
    if not sents:
        return ""
    return cap_chars(sorted(sents, key=len, reverse=True)[0], 220)


def build_qa_text(qa: Dict[str, Any], diag_fallback: str = "") -> str:
    qa = qa or {}
    industry = clean(qa.get("industry", ""))
    persona  = clean(qa.get("target_persona", ""))
    pain = clean(qa.get("pain_point", ""))

    solution = clean(
        qa.get("solution")
        or qa.get("service_definition")
        or qa.get("service_summary")
        or qa.get("service_overview")
        or ""
    )
    usp = clean(
        qa.get("usp")
        or qa.get("value_proposition")
        or qa.get("differentiator")
        or ""
    )
    pos = clean(
        qa.get("positioning")
        or qa.get("vision_headline")
        or qa.get("vision")
        or ""
    )
    stage = clean(str(qa.get("growth_stage", ""))) if qa.get("growth_stage") else ""

    head_parts = []
    if industry:
        head_parts.append(f"산업/카테고리는 {industry}이며")
    if persona:
        head_parts.append(f"주요 타깃은 {persona}이다.")
    else:
        head_parts.append("주요 타깃이 정의되어 있다.")
    s1 = " ".join(head_parts)

    body_parts = []
    if pain:
        body_parts.append(f"사용자는 {pain}을(를) 겪는다.")

    solved_bits = []
    if solution:
        solved_bits.append(solution)
    if usp:
        solved_bits.append(usp)

    if solved_bits:
        body_parts.append("이를 위해 " + " ".join(solved_bits) + "을(를) 제공한다.")
    else:
        core = extract_diag_core_sentence(diag_fallback) if diag_fallback else ""
        if core:
            body_parts.append(f"이를 위해 {core}")

    if pos:
        body_parts.append(f"포지셔닝은 {pos}이다.")
    if stage:
        body_parts.append(f"현재 단계는 {stage}이다.")

    out = clean(" ".join([s1, " ".join(body_parts)]))
    return force_1to2_sentences_kr(out, 360)


def build_naming_text(step2: Dict[str, Any], diag_text_for_bridge: str = "") -> str:
    step2 = step2 or {}
    a = (step2.get("analysis", {}) or {})
    o = (step2.get("output", {}) or {})

    parts = []
    if a.get("naming_direction"):
        parts.append(f"네이밍 방향: {a['naming_direction']}")
    if isinstance(a.get("keyword_extraction"), list) and a["keyword_extraction"]:
        parts.append("키워드: " + ", ".join([str(x) for x in a["keyword_extraction"][:10]]))
    if a.get("target_emotion"):
        parts.append(f"타깃 감정: {a['target_emotion']}")
    if o.get("brand_name"):
        parts.append(f"브랜드명: {o['brand_name']}")
    if o.get("name_rationale"):
        parts.append(f"선정 근거: {o['name_rationale']}")

    diag_core = extract_diag_core_sentence(diag_text_for_bridge) if diag_text_for_bridge else ""
    if a.get("target_emotion") and diag_core:
        parts.append(f"감정-기능 연결: {a['target_emotion']}을(를) 느끼는 과정에서, {diag_core}")
    elif diag_core:
        parts.append(f"기능 핵심 연결: {diag_core}")

    return clean(" ".join(parts))


def build_concept_text(step3: Dict[str, Any]) -> str:
    step3 = step3 or {}
    o = (step3.get("output", {}) or {})
    parts = []
    for k in ["concept_statement", "positioning"]:
        if o.get(k):
            parts.append(o[k])
    if isinstance(o.get("brand_values"), list) and o["brand_values"]:
        parts.append("브랜드 가치: " + ", ".join(o["brand_values"]))
    return clean(" ".join(parts))


def build_story_text(step4: Dict[str, Any]) -> str:
    step4 = step4 or {}
    o = (step4.get("output", {}) or {})
    return clean(o.get("brand_story", ""))


def build_step4_arc_and_messages(step4: Dict[str, Any]):
    step4 = step4 or {}
    o = (step4.get("output", {}) or {})
    arc = clean(o.get("narrative_arc", ""))
    msgs = o.get("core_messages", [])
    if not isinstance(msgs, list):
        msgs = []
    msgs = [clean(str(x)) for x in msgs if clean(str(x))]
    return arc, msgs


def build_step5_design_hints(step5: Dict[str, Any]) -> Dict[str, Any]:
    step5 = step5 or {}
    a = (step5.get("analysis", {}) or {})
    o = (step5.get("output", {}) or {})
    return {
        "design_style": a.get("design_style", ""),
        "color_preferences": a.get("color_preferences", []),
        "symbol_direction": a.get("symbol_direction", ""),
        "dalle_prompt": o.get("dalle_prompt", ""),
        "logo_concept": o.get("logo_concept", ""),
        "design_guidelines": o.get("design_guidelines", ""),
        "color_palette": o.get("color_palette", []),
    }
