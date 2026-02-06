# scripts/run_single.py
from Source.config import AppConfig, PathsConfig
from Source.model import load_models
from Source.pipeline.runner import run_single_brand
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

ENV_PATH = os.path.join(BASE_DIR, ".env")

QA_PATH  = os.path.join(BASE_DIR, "Test", "4o_test_brand_1to5", "step_1_diagnosis", "qa.json")
RAG_CONTEXT_PATH = os.path.join(BASE_DIR, "Test", "4o_test_brand_1to5", "rag_context.json")
FORCED_LOGO_PATH = os.path.join(BASE_DIR, "Test", "4o_test_brand_1to5", "step_5_logo", "test_brand_1to5_logo_1_20260130_003358.png")

SAVE_PATH_COMPACT = os.path.join(BASE_DIR, "Log", "Compact", "brand_consistency_compact.json")
SAVE_PATH_DEBUG   = os.path.join(BASE_DIR, "Log", "Debug", "brand_consistency_Debug.json")


def main():
    cfg = AppConfig(
        paths=PathsConfig(
            env_path=ENV_PATH,
            qa_path=QA_PATH,
            rag_context_path=RAG_CONTEXT_PATH,
            forced_logo_path=FORCED_LOGO_PATH,
            save_path_compact=SAVE_PATH_COMPACT,
            save_path_debug=SAVE_PATH_DEBUG,
        )
    )

    bundle = load_models(cfg)
    _ = run_single_brand(cfg, bundle)


if __name__ == "__main__":
    main()
