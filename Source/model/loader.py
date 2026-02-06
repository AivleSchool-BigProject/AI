"""
- .env 호출, HF 토큰 / OPENAI 키 확인
- device 선택 (Default = CPU)
- SBERT Embedding / HyperCLOVA 로드
- OPENAI Client 생성
- 모델 로딩 분리 → 실행/로직에서 로딩 코드 관여 불가
- 일자 : 2026-02-04
- 최초 개발자 : 김대호
"""

import os
import torch
from dataclasses import dataclass
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from openai import OpenAI
from ..config import AppConfig


@dataclass
class ModelBundle:
    device: str
    embed_model: SentenceTransformer
    clova_tokenizer: AutoTokenizer
    clova_model: AutoModelForCausalLM
    openai_client: OpenAI


def load_models(cfg: AppConfig) -> ModelBundle:
    load_dotenv(cfg.paths.env_path)

    hf_token = os.getenv("HUGGIG_KEY") or os.getenv("HUGGING_KEY") or os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("Missing HF token (HUGGIG_KEY / HUGGING_KEY / HF_TOKEN)")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY in env/.env")

    print("[LOAD] start")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("[LOAD] loading embed model")
    embed_model = SentenceTransformer(cfg.models.embed_model_id, device=device)
    print("[LOAD] embed model done")

    print("[LOAD] loading clova tokenizer/model")
    tokenizer = AutoTokenizer.from_pretrained(cfg.models.clova_model_id, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.models.clova_model_id,
        token=hf_token,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
    ).to(device)
    print("[LOAD] clova model done")
    print("[LOAD] openai client done")
    
    model.eval()

    oai = OpenAI(api_key=openai_api_key)

    return ModelBundle(
        device=device,
        embed_model=embed_model,
        clova_tokenizer=tokenizer,
        clova_model=model,
        openai_client=oai,
    )
