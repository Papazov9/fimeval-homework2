# ImageCLEF 2026 — Visual Open QA

Submission for the [ImageCLEF 2026 MultimodalReasoning — Visual OpenQA task](https://mbzuai-nlp.github.io/ImageCLEF-MultimodalReasoning/2026/).

Given an image that contains an exam question plus its visual content (diagram, chart, table, or figure), produce a free-form textual answer in the question's language.

## Reproducing a submission

The competition expects a single command on an A40 (40 GB) VM:

```bash
bash inference.sh
```

That installs dependencies, pulls the dataset from Hugging Face, runs the configured model on the test split, and writes `outputs/run.json` in the official submission format.

Environment variables understood by `inference.sh`:

| var | default | meaning |
|---|---|---|
| `MODEL` | `dummy` | predictor name: `dummy`, `qwen_vl`, `qwen_vl_tiny` |
| `MODEL_ID` | *predictor default* | HF model id override |
| `SPLIT` | `test` | dataset split (`train` / `dev` / `test`) |
| `OUTPUT` | `outputs/run.json` | output file |
| `MAX_NEW_TOKENS` | `64` | generation length cap |
| `LIMIT` | *unset* | if set, only run on the first N items (for sanity checks) |
| `INFERENCE_SKIP_INSTALL` | `0` | skip `pip install -r requirements.txt` |

Examples:

```bash
# Normal track (≥8B): Qwen2.5-VL-7B-Instruct (~8.3B total)
MODEL=qwen_vl bash inference.sh

# Tiny track (≤7B): Qwen2.5-VL-3B-Instruct (~3.75B)
MODEL=qwen_vl_tiny bash inference.sh

# Dev-split dry run on 20 items, then package as submission zip
MODEL=qwen_vl SPLIT=dev LIMIT=20 bash inference.sh
bash scripts/make_submission_zip.sh outputs/run.json outputs/submission.zip
```

The competition requires the final upload to be a zip file whose root contains a file literally named `run.json`. `scripts/make_submission_zip.sh` builds that layout from any `run.json` you point it at.

## Models

Both tracks use the same `QwenVLPredictor` (`src/models/qwen_vl.py`) with different backbones:

| predictor name | HF model id | params (total) | competition track |
|---|---|---|---|
| `qwen_vl` | `Qwen/Qwen2.5-VL-7B-Instruct` | ~8.3 B | Normal (≥ 8B) |
| `qwen_vl_tiny` | `Qwen/Qwen2.5-VL-3B-Instruct` | ~3.75 B | Tiny (≤ 7B) |
| `dummy` | — | — | debug (empty answers) |

Decoding is greedy (`do_sample=False`) for reproducibility. The prompt instructs the model to return only the final answer in the question's language, no reasoning.

## Repository layout

```
inference.sh                   entry point for the competition VM
requirements.txt
src/
  predict.py                   dataset → model → run.json
  models/
    base.py                    BasePredictor interface
    dummy.py                   empty-answer baseline
    qwen_vl.py                 Qwen2.5-VL (transformers)
  utils/
    language.py                ISO2 ↔ full-name mapping
  evaluation/
    evaluate_qa.py             official evaluator (vendored)
scripts/
  prepare_gold.py              HF dev split → gold JSON for the evaluator
  eval_dev.sh                  predict → prepare_gold → evaluate_qa on dev
  make_submission_zip.sh       bundle run.json into submission.zip
outputs/                       run.json, metrics, submission zips land here
```

## Evaluation

The official evaluator (`src/evaluation/evaluate_qa.py`, vendored from the starter kit) reports, overall and per-language:

- BLEU-1..4 (sacrebleu sentence-level) + `bleu_avg`
- ROUGE-1 / ROUGE-2 / ROUGE-L (rouge_score, stemmed f-measure)
- METEOR (nltk)
- COMET (`Unbabel/wmt22-comet-da`)

Run it on dev:

```bash
MODEL=qwen_vl bash scripts/eval_dev.sh
# → writes outputs/dev_qwen_vl.json, outputs/gold_dev.json, outputs/metrics_qwen_vl.json
```

## Dataset and external data

Only the competition dataset ([`SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual`](https://huggingface.co/datasets/SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual)) is used. It was adapted from [MBZUAI-IFM/EXAMS-V](https://huggingface.co/datasets/MBZUAI-IFM/EXAMS-V) by the organisers. No additional external datasets, no proprietary APIs.

Pre-trained VLM weights used:
- `Qwen/Qwen2.5-VL-7B-Instruct`
- `Qwen/Qwen2.5-VL-3B-Instruct`

## Licenses

- Dataset: CC-BY-NC-4.0 (non-commercial).
- `src/evaluation/evaluate_qa.py` is vendored from the official starter kit with attribution in its header.
- Qwen2.5-VL weights: see the respective HF model cards.
