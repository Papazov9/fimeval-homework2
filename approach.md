---
title: "ImageCLEF 2026 — Visual OpenQA"
subtitle: "Подход и резултати"
author: "[Име Фамилия], ФМИ"
date: "Май 2026"
lang: bg
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
fontsize: 11pt
geometry: margin=2.2cm
linkcolor: "blue"
---

# 1. Задача

Задачата **Visual OpenQA** от ImageCLEF 2026 MultimodalReasoning изисква от системата да отговори със свободен текст на изпитен въпрос, който е *вграден като изображение* заедно с асоцииран нему визуален елемент — диаграма, графика, таблица или фигура. Изходът е къс текстов отговор на езика на въпроса.

Входно-изходна спецификация:

- **Вход:** едно изображение `PIL.Image`, което съдържа както формулировката на въпроса, така и визуалния референт.
- **Изход:** низ — финалният отговор, без пояснения или разсъждения.
- **Метаданни:** уникален `question_id`, ISO-2 код на езика на въпроса.

Корпусът е получен чрез превръщане на multi-choice въпроси от EXAMS-V в open-ended формат, което означава, че референтните отговори са кратки именни фрази, числа или единични факти.

# 2. Данни

Използван е изключително официалният dataset `SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual` от Hugging Face (лиценз CC-BY-NC-4.0). Никакви външни данни и никакво допълнително обучение не са приложени.

| Split | Брой примери | Бележка |
|---|---|---|
| train | 528 | не се използва (без fine-tuning) |
| dev | 240 | за валидация и подбор на хиперпараметри |
| test | 439 | за официалното подаване |

Покрити езици: английски (en), български (bg), китайски (zh), хърватски (hr), италиански (it), сръбски (sr). Покрити предметни области: биология, химия, физика, социология.

# 3. Подход

## 3.1 Архитектурно решение

Избран е едностъпков подход: **един vision-language модел чете изображението директно и генерира отговор**. Не са използвани:

- отделен OCR за извличане на текст от изображението,
- retrieval-augmented компонент,
- ансамбли или multi-pass reasoning.

Мотивация: задачата има едно изображение на пример с малко контекст; добавянето на междинни стъпки увеличава риска от propagation на грешки без ясна полза, при условие че backbone-ът се справя с текст в изображения.

## 3.2 Модел

Като backbone е избран **Qwen2.5-VL-Instruct**, в две конфигурации:

| Track | Модел | Параметри |
|---|---|---|
| Normal (≥ 8B) | `Qwen/Qwen2.5-VL-7B-Instruct` | ~8.3 млрд. (включително visual encoder) |
| Tiny (≤ 7B) | `Qwen/Qwen2.5-VL-3B-Instruct` | ~3.75 млрд. |

Аргументи за избора:

- Qwen2.5-VL е публично достъпен с отворени тегла (изискване на състезанието).
- Има силна performance на multimodal benchmarks с диаграми и таблици — точно типът визуален елемент в нашия dataset.
- Подкрепя многоезичен изход; въпросите в dataset-а са на шест езика, а отговорите трябва да са на езика на въпроса.
- Побира се в 40 GB VRAM на A40 при `bfloat16` без quantization.

## 3.3 Промптване

Системният промпт е минимален и фокусиран върху форматирането на изхода:

```
The image contains an exam question together with a diagram,
chart, table, or figure. Answer the question in {language} with
ONLY the final answer — a short phrase, number, or a single
sentence. Do not restate the question. Do not show reasoning.
Do not add prefixes like 'The answer is'.
```

`{language}` е заместен с пълното английско име на езика (English, Bulgarian, Chinese, Croatian, Italian, Serbian). Изборът да се избягват chain-of-thought изходи е съзнателен — метриките BLEU и ROUGE наказват дълги изхода с допълнителни уводи („The answer is…“), а референтните отговори в корпуса са кратки спанове.

## 3.4 Декодиране

- **Greedy decoding** (`do_sample=False`).
- `max_new_tokens = 64`.
- Без temperature, без top-k/top-p sampling.

Мотивация: репродуцируемост (състезанието изисква едно и също подаване при повтаряне на изпълнението) и кратки изходи за съвместимост с BLEU/ROUGE.

# 4. Експериментална рамка

## 4.1 Среда на изпълнение

- GPU: NVIDIA A40 (40 GB VRAM) — изисквана конфигурация от организаторите.
- PyTorch + `transformers` (`Qwen2_5_VLForConditionalGeneration`).
- `device_map="auto"`, `torch_dtype="auto"` (bf16 при наличие).
- Единична команда за репродукция: `bash inference.sh`.

## 4.2 Метрики

Използва се официалният evaluator, vendored в `src/evaluation/evaluate_qa.py`:

- **BLEU-1, BLEU-2, BLEU-3, BLEU-4** и средно `bleu_avg` (sacrebleu, sentence-level).
- **ROUGE-1, ROUGE-2, ROUGE-L** (`rouge_score`, stemmed f-measure).
- **METEOR** (nltk).
- **COMET** (`Unbabel/wmt22-comet-da`) — neural quality estimation, multilingual.

Всяка метрика се изчислява глобално и per-language.

# 5. Резултати

Метриките по-долу са от пускане на `MODEL=qwen_vl bash scripts/eval_dev.sh` върху dev split (240 примера) на A40.

## 5.1 Общи резултати

| Метрика | Стойност |
|---|---|
| BLEU-1 | `[METRIC_BLEU_1]` |
| BLEU-2 | `[METRIC_BLEU_2]` |
| BLEU-3 | `[METRIC_BLEU_3]` |
| BLEU-4 | `[METRIC_BLEU_4]` |
| BLEU avg | `[METRIC_BLEU_AVG]` |
| ROUGE-1 | `[METRIC_ROUGE_1]` |
| ROUGE-2 | `[METRIC_ROUGE_2]` |
| ROUGE-L | `[METRIC_ROUGE_L]` |
| METEOR | `[METRIC_METEOR]` |
| COMET | `[METRIC_COMET]` |

## 5.2 Per-language резултати (BLEU avg / ROUGE-L / COMET)

| Език | BLEU avg | ROUGE-L | COMET | n |
|---|---|---|---|---|
| English | `[METRIC_EN_BLEU]` | `[METRIC_EN_ROUGE_L]` | `[METRIC_EN_COMET]` | 50 |
| Bulgarian | `[METRIC_BG_BLEU]` | `[METRIC_BG_ROUGE_L]` | `[METRIC_BG_COMET]` | 50 |
| Chinese | `[METRIC_ZH_BLEU]` | `[METRIC_ZH_ROUGE_L]` | `[METRIC_ZH_COMET]` | 50 |
| Croatian | `[METRIC_HR_BLEU]` | `[METRIC_HR_ROUGE_L]` | `[METRIC_HR_COMET]` | 50 |
| Italian | `[METRIC_IT_BLEU]` | `[METRIC_IT_ROUGE_L]` | `[METRIC_IT_COMET]` | 20 |
| Serbian | `[METRIC_SR_BLEU]` | `[METRIC_SR_ROUGE_L]` | `[METRIC_SR_COMET]` | 20 |

# 6. Обсъждане

`[DISCUSSION_PLACEHOLDER — попълва се след виждане на числата. Очаквани наблюдения:
(а) английският вероятно превъзхожда останалите езици заради разпределението в pretraining данните на Qwen;
(б) китайският може да е силно за BLEU, защото токенизацията по символи увеличава припокриването;
(в) кирилицата (bg, sr) и хърватският (hr) са най-вероятните губещи езици;
(г) COMET е по-устойчив към парафрази и обикновено е по-висок от BLEU.]`

# 7. Бъдеща работа

Възможни подобрения, които не са включени в текущата подаване:

- **Few-shot in-context prompting** с примерни (image, answer) двойки от train split, селектирани по сходство на езика/предметната област.
- **Self-consistency**: множествени генерирания с малък sampling temperature и majority vote на финалния отговор. Цена: 5–10× compute.
- **Lightweight fine-tuning** (LoRA) върху train split — необходимо е внимание към над-обучаване, защото train е само 528 примера.
- **Per-language prompt варианти**: малък frontmatter на езика на въпроса вместо английска инструкция, което може да помогне за not-en езиците.
- **OCR pre-pass** при по-стар или по-малък backbone, който се затруднява с текст в изображенията.

# 8. Възпроизводимост

Целият код е в repo-то, изпълнението е една команда:

```bash
# Normal track
MODEL=qwen_vl bash inference.sh

# Tiny track
MODEL=qwen_vl_tiny bash inference.sh

# Dev evaluation (BLEU/ROUGE/METEOR/COMET)
MODEL=qwen_vl bash scripts/eval_dev.sh
```

Без външни данни. Всички тегла се теглят автоматично от Hugging Face Hub при първото изпълнение.

# 9. Лицензи и източници

- Dataset: CC-BY-NC-4.0 (`SU-FMI-AI/ImageCLEF-MR2026-OpenQA-Visual`).
- Тегла на модела: вижте картата на модела `Qwen/Qwen2.5-VL-7B-Instruct` и `Qwen/Qwen2.5-VL-3B-Instruct`.
- `src/evaluation/evaluate_qa.py` е vendored от официалния starter kit на организаторите (`mbzuai-nlp/ImageCLEF-MultimodalReasoning`) с атрибуция в header-а на файла.
