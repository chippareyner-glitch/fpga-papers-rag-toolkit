"""Search Vivado PDF manuals with semantic + BM25 and output concise citations.

Usage: python search.py "report_timing -pba_mode" --top-k 4 --max-chars 900
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict

from rag_common import get_collection, get_model, keywords


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Search local Vivado documentation.')
    parser.add_argument('question', help='Your search query; Chinese and English both work.')
    parser.add_argument('--top-k', type=int, default=4, help='Max cited passages (default: 4).')
    parser.add_argument('--max-chars', type=int, default=900, help='Characters per passage (default: 900).')
    parser.add_argument('--mode', choices=['hybrid', 'semantic', 'keyword'], default='hybrid')
    parser.add_argument('--json', action='store_true', help='Machine-readable result for Codex.')
    args = parser.parse_args()
    top_k = max(1, min(args.top_k, 15))
    max_chars = max(200, min(args.max_chars, 5000))

    _, collection = get_collection()
    count = collection.count()
    if count == 0:
        print('Index empty. Add PDF manuals into documents/ and run: python build_index.py', file=sys.stderr)
        return 2

    pool = min(count, max(24, top_k * 6))
    scores = defaultdict(float)
    details = {}
    if args.mode in ('hybrid', 'semantic'):
        model = get_model()
        query_vector = model.encode(['query: ' + args.question], normalize_embeddings=True)[0]
        result = collection.query(query_embeddings=[query_vector.tolist()],
                                  n_results=pool,
                                  include=['documents', 'metadatas', 'distances'])
        for rank, (id_, doc, meta) in enumerate(zip(result['ids'][0],
                       result['documents'][0], result['metadatas'][0]), start=1):
            scores[id_] += 1.0 / (60 + rank)
            details[id_] = (doc, meta)

    if args.mode in ('hybrid', 'keyword'):
        from rank_bm25 import BM25Okapi
        # This loads local text only; it is never transmitted to Codex or an API.
        all_docs = collection.get(include=['documents', 'metadatas'])
        tokenized = [keywords(x) for x in all_docs['documents']]
        query_tokens = keywords(args.question)
        if query_tokens:
            bm25 = BM25Okapi(tokenized)
            raw_scores = bm25.get_scores(query_tokens)
            positions = sorted(range(len(raw_scores)), key=lambda i: raw_scores[i], reverse=True)
            rank = 0
            for i in positions:
                if raw_scores[i] <= 0 or rank >= pool:
                    break
                rank += 1
                id_ = all_docs['ids'][i]
                scores[id_] += 1.0 / (60 + rank)
                details[id_] = (all_docs['documents'][i], all_docs['metadatas'][i])

    ranked = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_k]
    hits = []
    for rank, id_ in enumerate(ranked, start=1):
        doc, meta = details[id_]
        hits.append({
            'rank': rank, 'source': meta.get('source', ''),
            'pdf_page': meta.get('page', None), 'official_url': meta.get('url', ''),
            'text': doc[:max_chars] + (' ... [truncated]' if len(doc) > max_chars else ''),
        })
    if args.json:
        print(json.dumps({'question': args.question, 'hits': hits},
                         ensure_ascii=False, indent=2))
    else:
        if not hits:
            print('No matches; try --mode semantic or a different query.')
        for h in hits:
            print(f"\n[{h['rank']}] {h['source']} | PDF page {h['pdf_page']}")
            if h['official_url']:
                print(f"Official guide: {h['official_url']}")
            print(h['text'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
