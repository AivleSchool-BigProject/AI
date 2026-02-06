"""
- cosine / topk cosine / verdict / score_pair 라우팅
- TEXT / IMAGE 평가에 대한 동일하게 접근 가능하도록 Adapter 개념
- 정책 변경시 config.py 수정
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
import torch
from typing import Optional, Dict, Any
from ..config import PolicyConfig
from ..preprocessing.text_utils import sent_candidates


def cosine(embed_model, a: str, b: str) -> float:
    e = embed_model.encode([a, b], normalize_embeddings=True)
    return float((e[0] * e[1]).sum())


def cosine_topk(embed_model, previous_output: str, current_output: str, k: int) -> float:
    P = sent_candidates(previous_output, max_sents=22)
    C = sent_candidates(current_output, max_sents=22)
    if not P or not C:
        return cosine(embed_model, previous_output, current_output)
    EP = torch.tensor(embed_model.encode(P, normalize_embeddings=True))
    EC = torch.tensor(embed_model.encode(C, normalize_embeddings=True))
    sim = EP @ EC.T
    best_vals, _ = torch.max(sim, dim=1)
    k = min(k, best_vals.size(0))
    return float(torch.topk(best_vals, k).values.mean())


def verdict(policy: PolicyConfig, pair: str, sim: float) -> str:
    p, r = policy.pair_thresholds[pair]
    return "PASS" if sim >= p else "REVIEW" if sim >= r else "FAIL"


def score_text_pair(embed_model, policy: PolicyConfig, pair: str, previous_output: str, current_output: str) -> float:
    pol = policy.scoring_policy[pair]
    if pol["method"] == "full":
        return cosine(embed_model, previous_output, current_output)
    return (
        cosine_topk(embed_model, previous_output, current_output, pol["k"]) +
        cosine_topk(embed_model, current_output, previous_output, pol["k"])
    ) / 2.0


def score_pair(embed_model, policy: PolicyConfig, pair: str,
               previous_output: str, current_output: str,
               semantic_state: Optional[Dict[str, Any]] = None) -> float:
    pol = policy.scoring_policy[pair]
    if pol["method"] in ("full", "topk"):
        return score_text_pair(embed_model, policy, pair, previous_output, current_output)
    if pol["method"] == "semantic":
        if (not semantic_state) or semantic_state.get("error") == "eval_error":
            return 0.0
        return float(semantic_state["semantic_scores"]["semantic_score"])
    return 0.0
