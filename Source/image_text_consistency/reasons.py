"""Logo (STEP4→LOGO) semantic-only reasons.

- fixed 3 points based on verdict
- uses semantic_state summary fields (semantic_scores / raw_head / errors)

Date: 2026-02-04
"""

from typing import Dict, Any, List


def make_logo_rule_points_semantic(verdict_value: str) -> List[str]:
    if verdict_value == "FAIL":
        return [
            "의미 충돌: 로고가 전달하는 핵심 의미가 narrative_arc/core_messages의 의도와 어긋남",
            "톤 불일치: 로고의 인상이 브랜드 톤(감성)과 다르게 해석됨",
            "근거 약함: 의미 연결을 뒷받침하는 단서가 부족해 해석이 불안정함",
        ]
    if verdict_value == "REVIEW":
        return [
            "부분 일치: 로고 의미가 일부 메시지와 연결되나 커버리지가 제한됨",
            "톤 부분 일치: 전반 톤은 유사하나 특정 감성이 약하게 전달됨",
            "해석 변동 가능: 의미/톤 단서가 충분히 풍부하지 않아 판단 변동 여지가 있음",
        ]
    return [
        "의미 일치: 로고 의미가 narrative_arc/core_messages와 자연스럽게 연결됨",
        "톤 일치: 로고 톤이 브랜드 톤과 유사하게 해석됨",
        "단서 충분: 의미 연결을 지지하는 단서가 비교적 풍부함",
    ]


def generate_reasons_logo_semantic(verdict_value: str, semantic_state: Dict[str, Any]) -> Dict[str, Any]:
    locked_points = make_logo_rule_points_semantic(verdict_value)

    if not isinstance(semantic_state, dict) or semantic_state.get("error") == "eval_error":
        errors = (semantic_state or {}).get("errors", {})
        e1 = f"OpenAI 응답에서 JSON 추출이 실패해 의미 추출이 불가했다(errors={errors})."
        e2 = "의미/톤 리스트가 비어 있어 점수가 0으로 계산되었다."
        meta_brand = (semantic_state or {}).get("raw_head", {}).get("meta_brand", {})
        meta_logo = (semantic_state or {}).get("raw_head", {}).get("meta_logo_sem", {})
        e3 = f"meta_brand={meta_brand}, meta_logo_sem={meta_logo}를 확인해야 한다."
        return {"reasons": [
            {"point": locked_points[0], "evidence": e1},
            {"point": locked_points[1], "evidence": e2},
            {"point": locked_points[2], "evidence": e3},
        ]}

    sc = semantic_state.get("semantic_scores", {})
    e1 = f"narrative_arc와 core_messages 의미 커버리지 평균으로 core_rate={sc.get('core_rate')}를 산정했다(arc_rate={sc.get('arc_rate')}, message_rate={sc.get('message_rate')})."
    e2 = f"brand_tone과 logo_tone 유사도로 tone_rate={sc.get('tone_rate')}를 확인했다."
    e3 = f"avoid 의미 유사 기반 패널티로 penalty={sc.get('penalty')}가 반영되었다(avoid_hit_sim={sc.get('avoid_hit_sim')}, cap={sc.get('avoid_penalty_cap')})."
    return {"reasons": [
        {"point": locked_points[0], "evidence": e1},
        {"point": locked_points[1], "evidence": e2},
        {"point": locked_points[2], "evidence": e3},
    ]}
