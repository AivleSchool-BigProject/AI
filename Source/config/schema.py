"""
- PATH, MODEL_ID, Threshold, Scoring Policy, Semantic cfg를 Class 관리
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any


@dataclass
class PathsConfig:
    env_path: str
    qa_path: str
    rag_context_path: str
    forced_logo_path: str
    save_path_compact: str
    save_path_debug: str
    logo_tmp_path: str = "/content/_tmp_logo_semantic.png"

    @property
    def log_txt_path(self) -> str:
        return self.save_path_debug.replace(".json", ".log.txt")


@dataclass
class ModelConfig:
    clova_model_id: str = "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B"
    embed_model_id: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    openai_model_vision: str = "gpt-5-mini"
    openai_model_text: str = "gpt-5-mini"


@dataclass
class PolicyConfig:
    pair_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "QA_TO_DIAG":        (0.65, 0.55),
        "DIAG_TO_NAMING":    (0.70, 0.60),
        "NAMING_TO_CONCEPT": (0.70, 0.60),
        "CONCEPT_TO_STORY":  (0.68, 0.58),
        "STEP4_TO_LOGO_SEMANTIC": (0.65, 0.50),
    })

    scoring_policy: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "QA_TO_DIAG":        {"method": "full"},
        "DIAG_TO_NAMING":    {"method": "topk", "k": 3},
        "NAMING_TO_CONCEPT": {"method": "topk", "k": 2},
        "CONCEPT_TO_STORY":  {"method": "topk", "k": 2},
        "STEP4_TO_LOGO_SEMANTIC": {"method": "semantic"},
    })


@dataclass
class SwitchConfig:
    use_diag_normalization: bool = True
    run_semantic_eval: bool = True
    save_debug_artifacts: bool = True
    write_debug_log_file: bool = True

    enable_logo_resize: bool = True
    logo_max_side: int = 768


@dataclass
class SemanticConfig:
    w_core: float = 0.75
    w_tone: float = 0.25
    avoid_penalty_per_hit: float = 0.10
    avoid_penalty_cap: float = 0.15
    avoid_hit_sim: float = 0.85
    max_core_items: int = 10
    max_tone_items: int = 10
    max_avoid_items: int = 10


@dataclass
class AppConfig:
    paths: PathsConfig
    models: ModelConfig = field(default_factory=ModelConfig)
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    switches: SwitchConfig = field(default_factory=SwitchConfig)
    semantic: SemanticConfig = field(default_factory=SemanticConfig)

    compact_id: str = "single_brand_semantic_only_result"
    debug_id: str = "single_brand_semantic_only_debug"
