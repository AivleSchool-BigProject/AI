"""Scoring router: unify text-consistency and image-text-consistency under one interface."""

from typing import Optional, Dict, Any
from ..config import AppConfig
from ..text_consistency.scoring import score_text_pair


def verdict(cfg: AppConfig, pair: str, sim: float) -> str:
    p, r = cfg.policy.pair_thresholds[pair]
    return "PASS" if sim >= p else "REVIEW" if sim >= r else "FAIL"


def score_pair(cfg: AppConfig, pair: str, previous_output: str, current_output: str,
              *, embed_model, semantic_state: Optional[Dict[str, Any]] = None) -> float:
    method = cfg.policy.scoring_policy[pair]["method"]

    if method in ("full", "topk"):
        return score_text_pair(embed_model, cfg.policy, pair, previous_output, current_output)

    if method == "semantic":
        if not semantic_state or semantic_state.get("error") == "eval_error":
            return 0.0
        return float(semantic_state.get("semantic_scores", {}).get("semantic_score", 0.0))

    return 0.0
