"""Shared configuration and utilities for the local Vivado documentation RAG."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCUMENTS = ROOT / 'documents'
DATABASE = ROOT / 'database'
MODEL_NAME = 'intfloat/multilingual-e5-small'
COLLECTION_NAME = 'vivado_e5_small_v1'
CHUNK_TOKENS = 300  # Stay below the embedding model's 512-token limit.
OVERLAP_TOKENS = 40

OFFICIAL_URLS = {
    'UG470': 'https://docs.amd.com/v/u/en-US/ug470_7Series_Config',
    'UG471': 'https://docs.amd.com/v/u/en-US/ug471_7Series_SelectIO',
    'UG472': 'https://docs.amd.com/v/u/en-US/ug472_7Series_Clocking',
    'UG473': 'https://docs.amd.com/v/u/en-US/ug473_7Series_Memory_Resources',
    'UG474': 'https://docs.amd.com/r/en-US/ug474_7Series_CLB',
    'UG476': 'https://docs.amd.com/v/u/en-US/ug476_7Series_Transceivers',
    'UG479': 'https://docs.amd.com/v/u/en-US/ug479_7Series_DSP48E1',
    'UG480': 'https://docs.amd.com/r/en-US/ug480_7Series_XADC',
    'UG586': 'https://docs.amd.com/r/en-US/ug586_7Series_MIS',
    'UG835': 'https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands',
    'UG892': 'https://docs.amd.com/r/en-US/ug892-vivado-design-flows-overview',
    'UG894': 'https://docs.amd.com/r/en-US/ug894-vivado-tcl-scripting',
    'UG900': 'https://docs.amd.com/r/en-US/ug900-vivado-logic-simulation',
    'UG901': 'https://docs.amd.com/r/en-US/ug901-vivado-synthesis',
    'UG902': 'https://docs.amd.com/r/en-US/ug902-vivado-high-level-synthesis',
    'UG903': 'https://docs.amd.com/r/en-US/ug903-vivado-using-constraints',
    'UG904': 'https://docs.amd.com/r/en-US/ug904-vivado-implementation',
    'UG906': 'https://docs.amd.com/r/en-US/ug906-vivado-design-analysis',
    'UG912': 'https://docs.amd.com/r/en-US/ug912-vivado-properties',
    'UG949': 'https://docs.amd.com/r/en-US/ug949-vivado-design-methodology',
}


def source_link(filename: str) -> str:
    match = re.search(r'UG\d{3,4}', filename, re.IGNORECASE)
    return OFFICIAL_URLS.get(match.group().upper(), '') if match else ''


def get_collection():
    import chromadb
    DATABASE.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DATABASE))
    # Embeddings are explicitly provided, so Chroma's default embedding model is NOT used.
    coll = client.get_or_create_collection(name=COLLECTION_NAME)
    return client, coll


def get_model():
    import os
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    # Works without CUDA; set RAG_DEVICE=cuda to opt into GPU explicitly.
    return SentenceTransformer(MODEL_NAME, device=os.getenv('RAG_DEVICE', 'cpu'))


def segment_text(text: str, tokenizer):
    """Yield original-text segments using tokenizer offsets, not character guesses."""
    text = text.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
    if len(text.strip()) < 40:
        return
    offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True,
                        truncation=False)['offset_mapping']
    stride = CHUNK_TOKENS - OVERLAP_TOKENS
    for i in range(0, len(offsets), stride):
        batch = offsets[i:i + CHUNK_TOKENS]
        if not batch:
            break
        start, end = batch[0][0], batch[-1][1]
        snippet = text[start:end].strip()
        if len(snippet) >= 40:
            yield snippet
        if i + CHUNK_TOKENS >= len(offsets):
            break


TOKEN_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_.-]*|\d+|[\u4e00-\u9fff]')


def keywords(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())
