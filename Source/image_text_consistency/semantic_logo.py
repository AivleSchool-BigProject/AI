"""
- OpenaAI Response JSON 추출 로직
- 로고 의미/톤 추출 => Prompt
- STEP4 브랜드 의미 (arc, messages) 추출 => Prompt
- SBRERT로 arc_rate/message_rate/tone_rate 계산 + avoid penalty 적용
- STEP4→LOGO semantic-only 가 독립 모듈
- 추후 의미분석 모델 교체, 프롬프트 개선시 해당 코드 수정
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
import base64
import json
import torch
from typing import Dict, Any, List, Tuple
from ..preprocessing.text_utils import clean, cap_chars, extract_first_json_object
from ..config import SemanticConfig, ModelConfig


OPENAI_JSON_SYSTEM = """
You are a strict extractor.
Return ONLY valid JSON.
No explanations.
No markdown.
No code fences.
The output MUST be a JSON object.
""".strip()

OPENAI_JSON_SYSTEM_RETRY = """
Return ONLY a JSON object and nothing else.
No extra text.
No markdown.
No code fences.
If uncertain, return {}.
""".strip()


def _img_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return "data:image/png;base64," + b64


def _resp_to_dict(resp) -> Dict[str, Any]:
    try:
        if hasattr(resp, "model_dump"):
            return resp.model_dump()
        if hasattr(resp, "to_dict"):
            return resp.to_dict()
    except Exception:
        pass
    try:
        return json.loads(str(resp))
    except Exception:
        return {}


def _collect_text_from_responses_dict(d: Dict[str, Any]) -> str:
    if not isinstance(d, dict):
        return ""
    out = []
    outputs = d.get("output", [])
    if isinstance(outputs, list):
        for item in outputs:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "message":
                continue
            content = item.get("content", [])
            if isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") in ("output_text", "text"):
                        t = c.get("text")
                        if isinstance(t, str) and t.strip():
                            out.append(t.strip())
    ot = d.get("output_text")
    if isinstance(ot, str) and ot.strip():
        out.append(ot.strip())
    return clean("\n".join(out))


def _extract_json_from_text(raw_text: str) -> Tuple[bool, str, Dict[str, Any]]:
    js = extract_first_json_object(raw_text or "")
    if not js:
        return False, "", {}
    try:
        obj = json.loads(js)
        if isinstance(obj, dict):
            return True, js, obj
        return False, js, {}
    except Exception:
        return False, js, {}


def openai_generate_json(oai_client, model_name: str, user_content_parts: list,
                        max_output_tokens: int = 1600, retry_on_no_json: bool = True) -> Dict[str, Any]:
    resp = oai_client.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": OPENAI_JSON_SYSTEM},
            {"role": "user", "content": user_content_parts},
        ],
        max_output_tokens=max_output_tokens,
    )
    d = _resp_to_dict(resp)
    status = d.get("status", "")
    raw_text = _collect_text_from_responses_dict(d)
    ok_json, js, obj = _extract_json_from_text(raw_text)

    retry_meta = {"did_retry": False, "retry_ok_json": False, "retry_status": "", "retry_max_output_tokens": None}

    if retry_on_no_json and (not ok_json):
        try:
            resp2 = oai_client.responses.create(
                model=model_name,
                input=[
                    {"role": "system", "content": OPENAI_JSON_SYSTEM_RETRY},
                    {"role": "user", "content": user_content_parts},
                ],
                max_output_tokens=int(max_output_tokens + 800),
            )
            d2 = _resp_to_dict(resp2)
            status2 = d2.get("status", "")
            raw_text2 = _collect_text_from_responses_dict(d2)
            ok_json2, js2, obj2 = _extract_json_from_text(raw_text2)

            retry_meta["did_retry"] = True
            retry_meta["retry_ok_json"] = bool(ok_json2)
            retry_meta["retry_status"] = status2
            retry_meta["retry_max_output_tokens"] = int(max_output_tokens + 800)

            if ok_json2:
                d = d2
                status = status2
                raw_text = raw_text2
                ok_json, js, obj = ok_json2, js2, obj2
        except Exception as e:
            retry_meta["did_retry"] = True
            retry_meta["retry_ok_json"] = False
            retry_meta["retry_error"] = repr(e)

    meta = {
        "status": status,
        "has_text": bool((raw_text or "").strip()),
        "max_output_tokens": max_output_tokens,
        "ok_json": bool(ok_json),
        "retry": retry_meta,
    }

    return {
        "meta": meta,
        "raw_text": (raw_text or "")[:1200],
        "json_str": js,
        "obj": obj if ok_json else {},
        "resp_dict_keys": list(d.keys()) if isinstance(d, dict) else [],
    }


def build_brand_semantic_prompt(cfg: SemanticConfig, arc_text: str, core_messages: list,
                                design_style: str, color_preferences: list) -> str:
    msgs = "\n".join([f"- {cap_chars(m, 200)}" for m in (core_messages or [])[:8]])
    cp = ", ".join([clean(str(x)) for x in (color_preferences or []) if clean(str(x))])[:120]
    return f"""
Return JSON only.

Task:
Extract the BRAND meanings from narrative_arc and core_messages.
Do NOT use brand_story.
Do NOT invent new meanings that are not supported by the input.

Schema:
{{
  "arc_meanings": [string],
  "message_meanings": [string],
  "tone": [string],
  "avoid_meanings": [string]
}}

Rules:
- English only.
- Each item is a short phrase (2~5 words).
- Deduplicate.
- Keep lists short: arc_meanings <= {cfg.max_core_items}, message_meanings <= {cfg.max_core_items},
  tone <= {cfg.max_tone_items}, avoid_meanings <= {cfg.max_avoid_items}.
- avoid_meanings: meanings we want to avoid.

INPUT:
narrative_arc:
{cap_chars(arc_text, 900)}

core_messages:
{msgs if msgs.strip() else "- (none)"}

extra style hints:
design_style: {cap_chars(design_style, 120)}
color_preferences: {cp}
""".strip()


def build_logo_semantic_prompt(cfg: SemanticConfig) -> str:
    return f"""
Return JSON only.

Task:
Infer the LOGO implied meanings and tone from the logo image.
Be conservative. If unsure, omit.

Schema:
{{
  "implied_meanings": [string],
  "tone": [string],
  "avoid_meanings": [string]
}}

Rules:
- English only.
- Each item is a short phrase (2~5 words).
- Deduplicate.
- implied_meanings <= {cfg.max_core_items}, tone <= {cfg.max_tone_items}, avoid_meanings <= {cfg.max_avoid_items}.
""".strip()


def _limit_list(xs, n: int) -> List[str]:
    if not isinstance(xs, list):
        return []
    out, seen = [], set()
    for x in xs:
        t = clean(str(x))
        if not t:
            continue
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
        if len(out) >= n:
            break
    return out


def _best_sims(embed_model, req_list: List[str], cand_list: List[str]) -> Tuple[List[Dict[str, Any]], float]:
    req_list = [clean(x) for x in (req_list or []) if clean(x)]
    cand_list = [clean(x) for x in (cand_list or []) if clean(x)]
    if not req_list or not cand_list:
        return [], 0.0

    Ereq = torch.tensor(embed_model.encode(req_list, normalize_embeddings=True))
    Ecand = torch.tensor(embed_model.encode(cand_list, normalize_embeddings=True))
    sim = Ereq @ Ecand.T
    best_vals, best_idx = torch.max(sim, dim=1)

    hits, vals = [], []
    for i, r in enumerate(req_list):
        j = int(best_idx[i])
        s = float(best_vals[i])
        hits.append({"req": r, "best": cand_list[j], "sim": round(s, 3)})
        vals.append(s)

    rate = float(sum(vals) / max(1, len(vals)))
    rate = max(0.0, min(1.0, rate))
    return hits, rate


def run_semantic_only(cfg_sem: SemanticConfig, cfg_models: ModelConfig,
                      oai_client, embed_model,
                      image_path: str,
                      arc_text: str, core_messages: list,
                      design_style: str, color_preferences: list) -> Dict[str, Any]:
    data_url = _img_to_data_url(image_path)

    logo_pack = openai_generate_json(
        oai_client=oai_client,
        model_name=cfg_models.openai_model_vision,
        user_content_parts=[
            {"type": "input_text", "text": build_logo_semantic_prompt(cfg_sem)},
            {"type": "input_image", "image_url": data_url}
        ],
        max_output_tokens=1200,
        retry_on_no_json=True
    )

    brand_pack = openai_generate_json(
        oai_client=oai_client,
        model_name=cfg_models.openai_model_text,
        user_content_parts=[
            {"type": "input_text", "text": build_brand_semantic_prompt(cfg_sem, arc_text, core_messages, design_style, color_preferences)}
        ],
        max_output_tokens=1200,
        retry_on_no_json=True
    )

    logo_obj = logo_pack["obj"] if logo_pack["meta"]["ok_json"] else {}
    brand_obj = brand_pack["obj"] if brand_pack["meta"]["ok_json"] else {}

    logo_implied = _limit_list(logo_obj.get("implied_meanings", []), cfg_sem.max_core_items)
    logo_tone    = _limit_list(logo_obj.get("tone", []), cfg_sem.max_tone_items)

    brand_arc    = _limit_list(brand_obj.get("arc_meanings", []), cfg_sem.max_core_items)
    brand_msgs   = _limit_list(brand_obj.get("message_meanings", []), cfg_sem.max_core_items)
    brand_tone   = _limit_list(brand_obj.get("tone", []), cfg_sem.max_tone_items)
    brand_avoid  = _limit_list(brand_obj.get("avoid_meanings", []), cfg_sem.max_avoid_items)

    arc_hits, arc_rate = _best_sims(embed_model, brand_arc, logo_implied)
    msg_hits, msg_rate = _best_sims(embed_model, brand_msgs, logo_implied)
    core_rate = (arc_rate + msg_rate) / 2.0 if (brand_arc or brand_msgs) else 0.0

    tone_hits, tone_rate = _best_sims(embed_model, brand_tone, logo_tone)

    avoid_hits = []
    penalty = 0.0
    if brand_avoid and logo_implied:
        ah, _ = _best_sims(embed_model, brand_avoid, logo_implied)
        for h in ah:
            if h["sim"] >= cfg_sem.avoid_hit_sim:
                avoid_hits.append(h)
        penalty = min(cfg_sem.avoid_penalty_cap, cfg_sem.avoid_penalty_per_hit * len(avoid_hits))

    semantic_score = float(cfg_sem.w_core * core_rate + cfg_sem.w_tone * tone_rate - penalty)
    semantic_score = max(0.0, min(1.0, semantic_score))

    errors = {}
    if not logo_pack["meta"]["ok_json"]:
        errors["logo_semantic"] = logo_pack["meta"]["status"] or "no_json"
    if not brand_pack["meta"]["ok_json"]:
        errors["brand_semantic"] = brand_pack["meta"]["status"] or "no_json"

    if errors.get("logo_semantic") and errors.get("brand_semantic"):
        return {
            "error": "eval_error",
            "errors": errors,
            "raw_head": {
                "logo_sem_raw_head": (logo_pack["raw_text"] or "")[:800],
                "brand_raw_head": (brand_pack["raw_text"] or "")[:800],
                "meta_logo_sem": logo_pack["meta"],
                "meta_brand": brand_pack["meta"],
            }
        }

    return {
        "semantic_scores": {
            "semantic_score": round(semantic_score, 4),
            "arc_rate": round(arc_rate, 4),
            "message_rate": round(msg_rate, 4),
            "core_rate": round(core_rate, 4),
            "tone_rate": round(tone_rate, 4),
            "penalty": round(penalty, 4),
            "avoid_hit_sim": cfg_sem.avoid_hit_sim,
            "avoid_penalty_cap": cfg_sem.avoid_penalty_cap,
        },
        "semantic_matches": {
            "brand_arc_meanings": brand_arc,
            "brand_message_meanings": brand_msgs,
            "brand_tone": brand_tone,
            "brand_avoid_meanings": brand_avoid,
            "logo_implied_meanings": logo_implied,
            "logo_tone": logo_tone,
            "arc_hits": arc_hits,
            "message_hits": msg_hits,
            "tone_hits": tone_hits,
            "avoid_hits": avoid_hits,
        },
        "raw_head": {
            "logo_sem_raw_head": (logo_pack["json_str"] or logo_pack["raw_text"] or "")[:800],
            "brand_raw_head": (brand_pack["json_str"] or brand_pack["raw_text"] or "")[:800],
            "meta_logo_sem": logo_pack["meta"],
            "meta_brand": brand_pack["meta"],
        },
        "error": "",
    }
