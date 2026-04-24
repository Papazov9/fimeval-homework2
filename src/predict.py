import argparse
import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm

from src.models import get_predictor
from src.utils.language import to_full_language


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual")
    ap.add_argument("--split", default="test")
    ap.add_argument("--model", default="dummy")
    ap.add_argument("--model_id", default=None, help="HF model id (overrides predictor default)")
    ap.add_argument("--max_new_tokens", type=int, default=64)
    ap.add_argument("--output", default="outputs/run.json")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    ds = load_dataset(args.dataset, split=args.split)
    if args.limit is not None:
        ds = ds.select(range(min(args.limit, len(ds))))

    kwargs = {"max_new_tokens": args.max_new_tokens}
    if args.model_id:
        kwargs["model_id"] = args.model_id
    predictor = get_predictor(args.model, **kwargs)

    preds = []
    seen_ids = set()
    for row in tqdm(ds, desc=f"predict[{args.model}/{args.split}]"):
        qid = row["question_id"]
        if qid in seen_ids:
            raise ValueError(f"Duplicate question_id in dataset: {qid}")
        seen_ids.add(qid)

        answer = predictor.predict(image=row["image"], language=row["language"])
        if isinstance(answer, str):
            answers = [answer]
        else:
            answers = [str(a) for a in answer]

        preds.append({
            "question_id": qid,
            "answers": answers,
            "language": to_full_language(row["language"]),
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(preds, f, ensure_ascii=False, indent=2)
    tmp.replace(out)
    print(f"Wrote {len(preds)} predictions to {out}")


if __name__ == "__main__":
    main()
