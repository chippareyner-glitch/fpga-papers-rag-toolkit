"""Index downloaded AMD Vivado PDF manuals into local Chroma.

Usage: python build_index.py [--reset] [--force]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from rag_common import (
    COLLECTION_NAME, DATABASE, DOCUMENTS, get_collection, get_model,
    segment_text, source_link,
)


def main() -> int:
    parser = argparse.ArgumentParser(description='Create/update the Vivado RAG index.')
    parser.add_argument('--reset', action='store_true', help='Delete existing index before building.')
    parser.add_argument('--force', action='store_true', help='Re-index unchanged PDF files.')
    args = parser.parse_args()

    paths = sorted(p for p in DOCUMENTS.rglob('*') if p.is_file() and p.suffix.lower() == '.pdf')
    if not paths:
        print(f'No PDF files found in: {DOCUMENTS}', file=sys.stderr)
        print('Download an official AMD UG906 or UG903 PDF, and put it there first.', file=sys.stderr)
        return 2

    client, collection = get_collection()
    manifest_path = DATABASE / 'manifest.json'
    if manifest_path.exists() and not args.reset:
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            manifest = {}
    else:
        manifest = {}
    if args.reset:
        client.delete_collection(COLLECTION_NAME)
        _, collection = get_collection()
    print(f'Found {len(paths)} PDF(s), currently indexed {collection.count()} chunks.', flush=True)

    import pymupdf
    model = None
    count_new = 0
    for path in paths:
        source = path.relative_to(DOCUMENTS).as_posix()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        previous = collection.get(where={'source': source}, include=['metadatas'])
        old_ids = previous['ids']
        existing = previous.get('metadatas') or []
        recorded = manifest.get(source, {})
        if (not args.force and old_ids and existing and
                recorded.get('sha256') == sha and
                recorded.get('chunks') == len(old_ids) and
                all(m.get('sha256') == sha for m in existing)):
            print(f'SKIP unchanged: {source} ({len(old_ids)} chunks)', flush=True)
            continue

        try:
            with pymupdf.open(path) as pdf:
                if pdf.needs_pass:
                    print(f'SKIP password-protected: {source}', file=sys.stderr)
                    continue
                records = []
                skipped = 0
                if model is None:
                    print('Loading embedding model (first run also downloads it)...', flush=True)
                    model = get_model()
                for page_no, page in enumerate(pdf, start=1):
                    # Physical PDF page number, NOT the printed chapter page number.
                    raw = page.get_text('text', sort=True)
                    chunks = list(segment_text(raw, model.tokenizer))
                    if not chunks:
                        skipped += 1
                    for chunk_no, chunk in enumerate(chunks, start=1):
                        record_id = hashlib.sha256(
                            f'{source}|{sha}|{page_no}|{chunk_no}'.encode('utf-8')
                        ).hexdigest()
                        records.append((record_id, chunk, {
                            'source': source, 'page': page_no, 'chunk': chunk_no,
                            'sha256': sha, 'url': source_link(source),
                        }))
        except Exception as exc:
            print(f'ERROR opening {source}: {exc}', file=sys.stderr)
            continue

        if not records:
            print(f'WARNING: no extractable text in {source}; might need OCR.', file=sys.stderr)
            continue

        print(f'Indexing {source}: {len(records)} chunks; {skipped} empty/short pages.', flush=True)
        t0 = time.perf_counter()
        try:
            for offset in range(0, len(records), 24):
                batch = records[offset:offset+24]
                docs = [x[1] for x in batch]
                embeddings = model.encode(['passage: ' + x for x in docs],
                                          normalize_embeddings=True, batch_size=12,
                                          show_progress_bar=False)
                collection.upsert(ids=[x[0] for x in batch], documents=docs,
                                  metadatas=[x[2] for x in batch],
                                  embeddings=embeddings.tolist())
                if offset % 240 == 0:
                    print(f'  {min(offset + len(batch), len(records))}/{len(records)}', flush=True)
        except Exception as exc:
            print(f'ERROR indexing {source}: {exc}', file=sys.stderr)
            print('Partial new chunks may be present. Re-run to retry.', file=sys.stderr)
            return 1
        # Delete stale chunks only after the replacement has been successfully inserted.
        new_ids = {x[0] for x in records}
        stale = [old_id for old_id in old_ids if old_id not in new_ids]
        for offset in range(0, len(stale), 200):
            collection.delete(ids=stale[offset:offset+200])
        count_new += len(records)
        manifest[source] = {'sha256': sha, 'chunks': len(records)}
        temporary = manifest_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(manifest_path)
        print(f'  completed in {time.perf_counter()-t0:.1f}s', flush=True)

    print(f'DONE. Indexed/re-indexed {count_new} chunks. Total: {collection.count()} chunks.')
    print('Try: python search.py "What is the difference between GBA and PBA?"')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
