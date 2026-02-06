"""
- HyperCLOVA로 reason 생성 
( PASS : pass prompt, FAIL/REVIEW는 locked points + evidence only)
- diag 정규화도 여기서 진행 (normalize_diag_with_qa)
- logo semantic pair의 fixed 3-point reasons
- 스코어링(정량)과 사유 생성(정성)을 분리
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""

import json
import torch
from typing import Dict, Any, List, Tuple
from ..preprocessing.text_utils import (
    clean, cap_chars, extract_first_json_object,
    ensure_three_reason_dicts, has_duplicate_evidence, is_placeholder_reason_dicts,
    pick_distinct_evidences
)

SYSTEM_PROMPT = """
당신은 브랜드 컨설팅 산출물의 일관성(QA)을 점검하는 심사관이다.
너의 역할은 verdict를 정하는 것이 아니라, 이미 주어진 verdict에 대한 근거(reasons)를 작성하는 것이다.
절대 verdict를 변경하지 말라.

중요:
- 반드시 JSON 객체만 출력하라(추가 텍스트/코드펜스/설명 금지).
- 문자열 내부에 큰따옴표(")를 직접 넣지 말라.
- 출력 스키마를 반드시 지켜라.

출력 스키마(고정):
{
  "reasons": [
    {"point": "...", "evidence": "..."},
    {"point": "...", "evidence": "..."},
    {"point": "...", "evidence": "..."}
  ]
}
""".strip()

DIAG_NORMALIZE_PROMPT = """
당신은 브랜드 컨설팅 초기진단 요약을 '사용자 QA 입력'과 일관되게 재정규화하는 편집자다.

목표:
- 아래 [QA 입력]을 기준으로, [원본 진단 요약]을 1~2문장으로 재작성한다.
- 반드시 다음 4요소를 명시적으로 포함:
  1) 타깃(연령대/라이프스타일 중 하나)
  2) 핵심 페인
  3) 해결 방식
  4) 차별점(usp에서 1개 이상)
- 새로운 기능/타깃을 추가하지 말 것
- 원본과 QA에 없는 정보는 만들지 말 것

중요 출력 규칙:
- 절대 JSON 형식으로 쓰지 말 것
- 중괄호/대괄호 표기 금지
- 라벨(json/assistant 등) 금지

출력:
- 1~2문장 텍스트만 출력

[QA 입력]
{qa_text}

[원본 진단 요약]
{diag_text}
""".strip()


def build_pass_reason_prompt(previous_output: str, current_output: str, verdict_value: str) -> str:
    return f"""
[previous_output]
{previous_output}

[current_output]
{current_output}

verdict = "{verdict_value}"

규칙:
- PASS: previous_output에서 유지된 핵심 의미를 2~3개 point로 작성
- 각 point에 대해 evidence는 previous_output 또는 current_output에서 "완전한 문장 1개"를 그대로 복사
- evidence는 문장 중간에서 끊지 말 것
- 말줄임표(..., …) 금지
- 큰따옴표(") 직접 포함 금지
- JSON만 출력

출력 JSON:
{{"reasons":[{{"point":"...","evidence":"..."}},{{"point":"...","evidence":"..."}},{{"point":"...","evidence":"..."}}]}}
""".strip()


def build_evidence_only_prompt(previous_output: str, current_output: str, verdict_value: str, locked_points: List[str]) -> str:
    pts = "\n".join([f"- {p}" for p in locked_points])
    return f"""
[previous_output]
{previous_output}

[current_output]
{current_output}

verdict = "{verdict_value}"

아래 point 3개는 이미 확정이다. point를 바꾸지 말고 그대로 유지하라.
각 point에 대해 evidence로 "완전한 문장 1개"를 previous_output 또는 current_output에서 그대로 복사해 넣어라.
주의:
- evidence 3개는 가능한 서로 다른 문장 사용(동일 반복 금지)
- 문장 중간에서 끊지 말 것
- 말줄임표(..., …) 금지
- 큰따옴표(") 직접 포함 금지
- 반드시 JSON만 출력
- reasons 정확히 3개

확정 point:
{pts}

출력 JSON:
{{"reasons":[
  {{"point":"{locked_points[0]}","evidence":"..."}} ,
  {{"point":"{locked_points[1]}","evidence":"..."}} ,
  {{"point":"{locked_points[2]}","evidence":"..."}}
]}}
""".strip()


def llm_generate_json(clova_tokenizer, clova_model, device: str, prompt_text: str, max_new_tokens=260) -> Tuple[str, str]:
    inputs = clova_tokenizer.apply_chat_template(
        [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt_text}],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        gen = clova_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=clova_tokenizer.eos_token_id,
            pad_token_id=clova_tokenizer.pad_token_id,
        )

    cut = gen[0][inputs["input_ids"].shape[-1]:]
    raw = clova_tokenizer.decode(cut, skip_special_tokens=True)
    js = extract_first_json_object(raw)
    return raw, js


def llm_generate_text(clova_tokenizer, clova_model, device: str, prompt_text: str, max_new_tokens=220) -> str:
    inputs = clova_tokenizer.apply_chat_template(
        [{"role": "system", "content": "추가 설명 없이 텍스트만 출력한다. 코드펜스/백틱/라벨을 쓰지 않는다."},
         {"role": "user", "content": prompt_text}],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        gen = clova_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=clova_tokenizer.eos_token_id,
            pad_token_id=clova_tokenizer.pad_token_id,
        )

    cut = gen[0][inputs["input_ids"].shape[-1]:]
    raw = clova_tokenizer.decode(cut, skip_special_tokens=True)
    return clean(raw)


def normalize_diag_with_qa(qa_text: str, diag_text: str,
                          clova_tokenizer, clova_model, device: str,
                          force_1to2_fn) -> str:
    qa_text2 = (qa_text or "").replace("{", " ").replace("}", " ")
    diag_text2 = (diag_text or "").replace("{", " ").replace("}", " ")
    prompt = DIAG_NORMALIZE_PROMPT.format(qa_text=qa_text2, diag_text=diag_text2)
    try:
        t = llm_generate_text(clova_tokenizer, clova_model, device, prompt, max_new_tokens=200)
        return force_1to2_fn(t, max_chars=260)
    except Exception:
        return force_1to2_fn(diag_text, max_chars=260)


def make_rule_points_sbert(verdict_value: str) -> List[str]:
    if verdict_value == "FAIL":
        return [
            "누락: previous_output의 핵심 내용이 current_output에서 충분히 드러나지 않음",
            "불일치: current_output이 previous_output과 다른 주장/초점을 포함",
            "모호: 근거 문장 매칭이 약해 의미 연결이 불명확함",
        ]
    if verdict_value == "REVIEW":
        return [
            "부분 일치: 핵심 방향은 이어지나 일부 세부가 약함",
            "구체성 부족: previous_output의 구체 요소가 current_output에서 축약됨",
            "기능 연결 약함: 방향은 같지만 실행/차별 근거 연결이 약함",
        ]
    return [
        "핵심 의미 유지: previous_output의 주요 메시지가 current_output에서 유지됨",
        "요소 일치: 핵심 방향이 current_output에서도 확인됨",
        "표현 차이: 표현은 다르나 의미 연결이 확인됨",
    ]


def rule_reasons_sbert(verdict_value: str, previous_output: str, current_output: str) -> List[Dict[str, str]]:
    locked_points = make_rule_points_sbert(verdict_value)
    evs = pick_distinct_evidences(previous_output, current_output, max_chars=260)
    return [
        {"point": locked_points[0], "evidence": evs[0]},
        {"point": locked_points[1], "evidence": evs[1]},
        {"point": locked_points[2], "evidence": evs[2]},
    ]


def generate_reasons_text(previous_output: str, current_output: str, verdict_value: str,
                          clova_tokenizer, clova_model, device: str) -> Tuple[Dict[str, Any], str]:
    if verdict_value in ("FAIL", "REVIEW"):
        locked_points = make_rule_points_sbert(verdict_value)
        prompt = build_evidence_only_prompt(previous_output, current_output, verdict_value, locked_points)
        raw, js = llm_generate_json(clova_tokenizer, clova_model, device, prompt, max_new_tokens=280)
        try:
            obj = json.loads(js)
            reasons = ensure_three_reason_dicts(obj)
            for i in range(3):
                reasons[i]["point"] = locked_points[i]
                reasons[i]["evidence"] = cap_chars(reasons[i]["evidence"], 260)
            if (not is_placeholder_reason_dicts(reasons)) and (not has_duplicate_evidence(reasons)):
                return {"reasons": reasons}, raw
        except Exception:
            pass
        return {"reasons": rule_reasons_sbert(verdict_value, previous_output, current_output)}, raw

    raw1, js1 = llm_generate_json(clova_tokenizer, clova_model, device,
                                 build_pass_reason_prompt(previous_output, current_output, verdict_value),
                                 max_new_tokens=260)
    try:
        obj1 = json.loads(js1)
        reasons1 = ensure_three_reason_dicts(obj1)
        for i in range(3):
            reasons1[i]["evidence"] = cap_chars(reasons1[i]["evidence"], 260)
        if (not is_placeholder_reason_dicts(reasons1)) and (not has_duplicate_evidence(reasons1)):
            return {"reasons": reasons1}, raw1
    except Exception:
        pass
    return {"reasons": rule_reasons_sbert("PASS", previous_output, current_output)}, raw1


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

    if semantic_state.get("error") == "eval_error":
        errors = semantic_state.get("errors", {})
        e1 = f"OpenAI 응답에서 JSON 추출이 실패해 의미 추출이 불가했다(errors={errors})."
        e2 = "의미/톤 리스트가 비어 있어 점수가 0으로 계산되었다."
        meta_brand = semantic_state.get("raw_head", {}).get("meta_brand", {})
        meta_logo = semantic_state.get("raw_head", {}).get("meta_logo_sem", {})
        e3 = f"meta_brand={meta_brand}, meta_logo_sem={meta_logo}를 확인해야 한다."
        return {"reasons": [
            {"point": locked_points[0], "evidence": e1},
            {"point": locked_points[1], "evidence": e2},
            {"point": locked_points[2], "evidence": e3},
        ]}

    sc = semantic_state["semantic_scores"]
    e1 = f"narrative_arc와 core_messages 의미 커버리지 평균으로 core_rate={sc['core_rate']}를 산정했다(arc_rate={sc['arc_rate']}, message_rate={sc['message_rate']})."
    e2 = f"brand_tone과 logo_tone 유사도로 tone_rate={sc['tone_rate']}를 확인했다."
    e3 = f"avoid 의미 유사 기반 패널티로 penalty={sc['penalty']}가 반영되었다(avoid_hit_sim={sc.get('avoid_hit_sim')}, cap={sc.get('avoid_penalty_cap')})."
    return {"reasons": [
        {"point": locked_points[0], "evidence": e1},
        {"point": locked_points[1], "evidence": e2},
        {"point": locked_points[2], "evidence": e3},
    ]}
