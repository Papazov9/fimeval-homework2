import argparse
import json
from pathlib import Path

from datasets import load_dataset

from src.utils.language import to_full_language


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--output", default="outputs/gold_dev.json")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    ds = load_dataset(args.dataset, split=args.split)
    if args.limit is not None:
        ds = ds.select(range(min(args.limit, len(ds))))

    items = []
    for row in ds:
        items.append({
            "question_id": row["question_id"],
            "answers": [row["answer"]],
            "language": to_full_language(row["language"]),
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    tmp.replace(out)
    print(f"Wrote {len(items)} gold items to {out}")


if __name__ == "__main__":
    main()
