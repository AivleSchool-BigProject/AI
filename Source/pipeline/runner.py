# brand_qa/runner.py
"""
- 데이터 로드 → 텍스트 빌드 → (옵션) diag normalize → (옵션) semantic eval 
- pairs 생성 → scoring/verdict → reasons 생성
- out_compact/out_debug 생성 + run_meta 채우기 + save
- logo semantic pair의 fixed 3-point reasons
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""


import os
from typing import Dict, Any, List, Tuple

from ..config import AppConfig
from ..preprocessing.io import load_json, save_json, resolve_logo_path, resize_logo_if_needed, FileLogger
from ..preprocessing.text_builders import (
    build_diag_text, build_qa_text, build_naming_text,
    build_concept_text, build_story_text, build_step4_arc_and_messages,
    build_step5_design_hints,
)
from ..preprocessing.text_utils import force_1to2_sentences_kr
from ..image_text_consistency.semantic_logo import run_semantic_only
from .scoring_router import score_pair, verdict
from ..text_consistency.reasons import (
    normalize_diag_with_qa,
    generate_reasons_text,
)
from ..image_text_consistency.reasons import generate_reasons_logo_semantic


def run_single_brand(cfg: AppConfig, bundle) -> Dict[str, Any]:
    logger = FileLogger(cfg.paths.log_txt_path, enabled=cfg.switches.write_debug_log_file)

    qa = load_json(cfg.paths.qa_path)
    rc = load_json(cfg.paths.rag_context_path)

    diag_raw = build_diag_text(rc.get("step_1", {}))
    qa_text_raw = build_qa_text(qa, diag_fallback=diag_raw)

    if cfg.switches.use_diag_normalization:
        diag_text = normalize_diag_with_qa(
            qa_text_raw, diag_raw,
            bundle.clova_tokenizer, bundle.clova_model, bundle.device,
            force_1to2_fn=force_1to2_sentences_kr
        )
    else:
        diag_text = force_1to2_sentences_kr(diag_raw, 260)

    qa_text = qa_text_raw
    naming_text = build_naming_text(rc.get("step_2", {}), diag_text_for_bridge=diag_text)
    concept_text = build_concept_text(rc.get("step_3", {}))

    step4 = rc.get("step_4", {}) if isinstance(rc.get("step_4"), dict) else {}
    story_text = build_story_text(step4)

    arc_text, core_msgs = build_step4_arc_and_messages(step4)

    step5 = rc.get("step_5", {}) if isinstance(rc.get("step_5"), dict) else {}
    hints = build_step5_design_hints(step5)
    design_style = hints.get("design_style", "")
    color_preferences = hints.get("color_preferences", [])
    color_palette = hints.get("color_palette", [])

    rag_base_dir = os.path.dirname(cfg.paths.rag_context_path)
    orig_logo_path = resolve_logo_path(step5, rag_base_dir=rag_base_dir, forced_local=cfg.paths.forced_logo_path)

    resize_info = None
    logo_image_path = orig_logo_path
    if cfg.switches.enable_logo_resize and orig_logo_path and os.path.exists(orig_logo_path):
        resize_info = resize_logo_if_needed(orig_logo_path, cfg.paths.logo_tmp_path, max_side=cfg.switches.logo_max_side)
        if resize_info.get("ok") and os.path.exists(cfg.paths.logo_tmp_path):
            logo_image_path = cfg.paths.logo_tmp_path

    semantic_state = None
    if cfg.switches.run_semantic_eval and logo_image_path and os.path.exists(logo_image_path):
        try:
            semantic_state = run_semantic_only(
                cfg_sem=cfg.semantic,
                cfg_models=cfg.models,
                oai_client=bundle.openai_client,
                embed_model=bundle.embed_model,
                image_path=logo_image_path,
                arc_text=arc_text,
                core_messages=core_msgs,
                design_style=design_style,
                color_preferences=color_preferences,
            )
        except Exception as e:
            semantic_state = {"error": "eval_error", "errors": {"exception": repr(e)}}

    pairs: List[Tuple[str, str, str]] = [
        ("QA_TO_DIAG",        qa_text,      diag_text),
        ("DIAG_TO_NAMING",    diag_text,    naming_text),
        ("NAMING_TO_CONCEPT", naming_text,  concept_text),
        ("CONCEPT_TO_STORY",  concept_text, story_text),
    ]
    if cfg.switches.run_semantic_eval and (logo_image_path and os.path.exists(logo_image_path)):
        pairs.append(("STEP4_TO_LOGO_SEMANTIC", "STEP4_ARC+MESSAGES", logo_image_path))

    out_compact = {"id": cfg.compact_id, "pairs": []}
    out_debug = {
        "id": cfg.debug_id,
        "run_meta": {},
        "debug_texts": {
            "QA_TEXT": qa_text,
            "DIAG_TEXT_USED": diag_text,
            "NAMING_TEXT": naming_text,
            "CONCEPT_TEXT": concept_text,
            "STORY_TEXT": story_text,
            "STEP4_NARRATIVE_ARC_ONLY": arc_text,
            "STEP4_CORE_MESSAGES_ONLY": core_msgs,
            "STEP5_HINTS": {
                "design_style": design_style,
                "color_preferences": color_preferences,
                "color_palette": color_palette,
            },
            "ORIG_LOGO_PATH": orig_logo_path,
            "LOGO_IMAGE_PATH_USED": logo_image_path,
            "RESIZE_INFO": resize_info,
            "STEP4_TO_LOGO_SEMANTIC_FULL": semantic_state,
        }
    }

    scores = []
    for pair_name, previous_output, current_output in pairs:
        if pair_name == "STEP4_TO_LOGO_SEMANTIC":
            sim = score_pair(
                cfg,
                pair_name,
                previous_output,
                current_output,
                embed_model=bundle.embed_model,
                semantic_state=semantic_state,
            )
            v = verdict(cfg, pair_name, sim)
            scores.append(sim)

            reasons_obj = generate_reasons_logo_semantic(
                v,
                semantic_state if isinstance(semantic_state, dict) else {"error": "eval_error", "errors": {"state": "missing"}}
            )

            out_compact["pairs"].append({
                "pair": pair_name,
                "verdict": v,
                "reasons": reasons_obj["reasons"][:3],
                "cosine_similarity": round(float(sim), 3),
            })
            continue

        sim = score_pair(
            cfg,
            pair_name,
            previous_output,
            current_output,
            embed_model=bundle.embed_model,
        )
        v = verdict(cfg, pair_name, sim)
        scores.append(sim)

        reasons_obj, _raw = generate_reasons_text(
            previous_output, current_output, v,
            bundle.clova_tokenizer, bundle.clova_model, bundle.device
        )

        out_compact["pairs"].append({
            "pair": pair_name,
            "verdict": v,
            "reasons": reasons_obj["reasons"][:3],
            "cosine_similarity": round(float(sim), 3),
        })


    out_compact["total_cosine_similarity"] = round(sum(scores) / len(scores), 3) if scores else 0.0

    semantic_scores_summary = None
    semantic_meta_summary = None
    semantic_error = None

    if isinstance(semantic_state, dict):
        semantic_error = semantic_state.get("error")
        if semantic_state.get("error") != "eval_error":
            semantic_scores_summary = semantic_state.get("semantic_scores")
            semantic_meta_summary = {
                "meta_logo_sem": semantic_state.get("raw_head", {}).get("meta_logo_sem"),
                "meta_brand": semantic_state.get("raw_head", {}).get("meta_brand"),
            }
        else:
            semantic_meta_summary = semantic_state.get("errors")

    out_debug["run_meta"] = {
        "device": bundle.device,
        "paths": {
            "qa_path": cfg.paths.qa_path,
            "rag_context_path": cfg.paths.rag_context_path,
            "forced_logo_path": cfg.paths.forced_logo_path,
            "orig_logo_path": orig_logo_path,
            "logo_path_used": logo_image_path,
            "tmp_logo_path": cfg.paths.logo_tmp_path,
            "save_compact": cfg.paths.save_path_compact,
            "save_debug": cfg.paths.save_path_debug,
            "log_txt": cfg.paths.log_txt_path,
        },
        "logo": {
            "orig_exists": bool(orig_logo_path and os.path.exists(orig_logo_path)),
            "used_exists": bool(logo_image_path and os.path.exists(logo_image_path)),
            "resize_info": resize_info,
            "max_side": cfg.switches.logo_max_side,
        },
        "semantic": {
            "ran": bool(cfg.switches.run_semantic_eval and logo_image_path and os.path.exists(logo_image_path)),
            "error": semantic_error,
            "scores": semantic_scores_summary,
            "meta": semantic_meta_summary,
            "config": cfg.semantic.__dict__,
        },
        "switches": {
            "use_diag_normalization": cfg.switches.use_diag_normalization,
            "run_semantic_eval": cfg.switches.run_semantic_eval,
            "enable_logo_resize": cfg.switches.enable_logo_resize,
            "save_debug_artifacts": cfg.switches.save_debug_artifacts,
            "write_debug_log_file": cfg.switches.write_debug_log_file,
        }
    }

    save_json(cfg.paths.save_path_compact, out_compact, indent=2)
    if cfg.switches.save_debug_artifacts:
        save_json(cfg.paths.save_path_debug, out_debug, indent=2)

    logger.write("[DONE] saved_compact=" + cfg.paths.save_path_compact)
    if cfg.switches.save_debug_artifacts:
        logger.write("[DONE] saved_debug=" + cfg.paths.save_path_debug)
    logger.write("[DONE] saved_log=" + cfg.paths.log_txt_path)

    return out_compact
