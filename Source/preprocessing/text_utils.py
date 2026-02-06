"""
- 문자열 전처리 파일
- evidence 중복 / placeholder 체크
- reason 추출 문장 후보 풀 생성
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
import re
from typing import List, Dict, Any


def clean(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def cap_chars(t: str, max_chars=420):
    t = clean((t or "").replace("…", " ").replace("...", " ").replace("`", " "))
    if len(t) <= max_chars:
        return t
    cut = t[:max_chars]
    sp = cut.rfind(" ")
    return cut[:sp] if sp > 60 else cut


def extract_first_json_object(s: str) -> str:
    s = (s or "").strip()
    start = s.find("{")
    if start == -1:
        return ""
    depth, in_str, esc = 0, False, False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":  # escape
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start:i+1]
    return ""


def split_sents_kr(t: str) -> List[str]:
    t = clean(t)
    if not t:
        return []
    sents = re.split(r"(?<=[.!?])\s+", t)
    if len(sents) <= 1:
        sents = re.split(r"(?<=(다|요|함)\.)\s+|(?<=(다|요|함))\s+", t)
    sents = [clean(s) for s in sents if clean(s)]
    sents = [s for s in sents if len(s) >= 12]
    return sents


def sent_candidates(t: str, max_sents=18) -> List[str]:
    sents = split_sents_kr(t)
    if len(sents) <= max_sents:
        return sents
    head = sents[: max_sents // 2]
    tail = sorted(sents[max_sents // 2:], key=len, reverse=True)[: max_sents - len(head)]
    return head + tail


def strip_chat_artifacts(t: str) -> str:
    t = clean(t)
    t = re.sub(r"^\s*(json\s*)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\bassistant\b", "", t, flags=re.IGNORECASE)
    t = clean(t)
    t = t.replace("{", " ").replace("}", " ").replace("[", " ").replace("]", " ")
    return clean(t)


def force_1to2_sentences_kr(t: str, max_chars=260) -> str:
    t = strip_chat_artifacts(t)
    sents = split_sents_kr(t)
    if not sents:
        return cap_chars(t, max_chars)
    if len(sents) >= 2:
        return cap_chars(clean(sents[0] + " " + sents[1]), max_chars)
    return cap_chars(clean(sents[0]), max_chars)


def ensure_three_reason_dicts(obj: Dict[str, Any]) -> List[Dict[str, str]]:
    reasons = obj.get("reasons", [])
    if not isinstance(reasons, list) or len(reasons) == 0:
        return []
    fixed = []
    for r in reasons:
        if not isinstance(r, dict):
            continue
        p = clean(str(r.get("point", ""))).replace('"', "")
        e = clean(str(r.get("evidence", ""))).replace('"', "")
        p = cap_chars(p, 380)
        e = cap_chars(e, 260)
        if p:
            fixed.append({"point": p, "evidence": e})
    while len(fixed) < 3:
        fixed.append({"point": "모호: 근거 추출 부족으로 추가 확인 필요", "evidence": "근거 문장을 추가로 확인해야 합니다."})
    return fixed[:3]


def has_duplicate_evidence(reasons: List[Dict[str, str]]) -> bool:
    evs = [clean(r.get("evidence", "")) for r in (reasons or [])]
    evs = [e for e in evs if e]
    return len(evs) >= 2 and len(set(evs)) != len(evs)


def is_placeholder_reason_dicts(reasons: List[Dict[str, str]]) -> bool:
    bad = {"...", ".", "..", "…", "없음", "해당 없음", "N/A"}
    for r in reasons:
        p = clean(str(r.get("point", "")))
        e = clean(str(r.get("evidence", "")))
        if (not p) or (p in bad) or p.count(".") >= 3:
            return True
        if len(p) < 6:
            return True
        if (not e) or (len(e) < 12):
            return True
        if ("..." in e) or ("…" in e):
            return True
    return False


def pick_distinct_evidences(prev: str, curr: str, max_chars=260) -> List[str]:
    P = split_sents_kr(prev)
    C = split_sents_kr(curr)
    pools = [P, C, P + C]
    used, out = set(), []
    for pool in pools:
        for s in pool:
            ss = clean(s)
            if ss and ss not in used:
                used.add(ss)
                out.append(cap_chars(ss, max_chars))
                break
        if len(out) >= 3:
            break

    candidates = []
    for s in (P + C):
        ss = clean(s)
        if ss and ss not in used:
            candidates.append(ss)
    candidates.sort(key=len, reverse=True)
    for s in candidates:
        if len(out) >= 3:
            break
        used.add(s)
        out.append(cap_chars(s, max_chars))

    while len(out) < 3:
        out.append(cap_chars(clean(curr) or clean(prev), max_chars))

    if len(set(out)) < 3:
        out2, seen = [], {}
        for e in out:
            if e not in seen:
                seen[e] = 0
                out2.append(e)
            else:
                seen[e] += 1
                out2.append(clean(e + f" (근거#{seen[e]+1})"))
        out = out2[:3]
    return out[:3]
