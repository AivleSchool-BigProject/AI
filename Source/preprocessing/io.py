"""
- JSON Load/Save , 로고 경로, 로고 리사이즈, FileLogger
- 입출력/파일 시스템 관련
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
import json
import os
from typing import Any, Dict
from PIL import Image


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: Any, indent: int = 2) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def normalize_path(p: str) -> str:
    return (p or "").replace("\\", "/").strip()


def resolve_logo_path(step5: Dict[str, Any], rag_base_dir: str, forced_local: str = "") -> str:
    if forced_local and os.path.exists(forced_local):
        return forced_local

    step5 = step5 or {}
    out = (step5.get("output", {}) or {})
    raw = normalize_path(out.get("logo_image_path", "") or "")

    sel = out.get("selected_image_index", None)
    logos = out.get("logo_images", None)
    if isinstance(sel, int) and isinstance(logos, list) and 0 <= sel < len(logos):
        item = logos[sel]
        if isinstance(item, dict):
            cand = normalize_path(item.get("path", "") or "")
        else:
            cand = normalize_path(str(item) or "")
        if cand:
            raw = cand

    if raw and os.path.isabs(raw) and os.path.exists(raw):
        return raw

    if raw:
        cand = os.path.join(rag_base_dir, raw)
        if os.path.exists(cand):
            return cand
        cand2 = os.path.join(rag_base_dir, os.path.basename(raw))
        if os.path.exists(cand2):
            return cand2

    if raw and os.path.exists(os.path.basename(raw)):
        return os.path.basename(raw)

    return ""


def resize_logo_if_needed(src_path: str, dst_path: str, max_side: int = 768) -> Dict[str, Any]:
    info = {"ok": False, "src": src_path, "dst": dst_path, "orig_size": None, "new_size": None, "scale": None, "max_side": max_side}
    try:
        img = Image.open(src_path).convert("RGBA")
        w, h = img.size
        info["orig_size"] = [w, h]
        m = max(w, h)
        if m <= max_side:
            img.save(dst_path, format="PNG")
            info["ok"] = True
            info["new_size"] = [w, h]
            info["scale"] = 1.0
            return info

        scale = max_side / float(m)
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))
        img2 = img.resize((nw, nh), Image.LANCZOS)
        img2.save(dst_path, format="PNG")
        info["ok"] = True
        info["new_size"] = [nw, nh]
        info["scale"] = round(scale, 4)
        return info
    except Exception as e:
        info["error"] = repr(e)
        return info


class FileLogger:
    """print 없이 파일에만 쓰는 로거."""
    def __init__(self, log_path: str, enabled: bool = True):
        self.log_path = log_path
        self.enabled = enabled
        if self.enabled:
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass

    def write(self, line: str) -> None:
        if not self.enabled:
            return
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(str(line) + "\n")
                f.flush()
        except Exception:
            pass
