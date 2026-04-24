import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from src.utils.language import to_full_language
from .base import BasePredictor

_PROMPT = (
    "The image contains an exam question together with a diagram, chart, table, or figure. "
    "Answer the question in {language} with ONLY the final answer — a short phrase, number, "
    "or a single sentence. Do not restate the question. Do not show reasoning. "
    "Do not add prefixes like 'The answer is'."
)


class QwenVLPredictor(BasePredictor):
    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-VL-7B-Instruct",
        max_new_tokens: int = 64,
        dtype: str = "auto",
        **_,
    ):
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map="auto",
        ).eval()
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.max_new_tokens = max_new_tokens

    def predict(self, image, language: str) -> str:
        messages = [{
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": _PROMPT.format(language=to_full_language(language))},
            ],
        }]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.processor(
            text=[text],
            images=[image],
            padding=True,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            gen = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
            )
        gen = gen[:, inputs.input_ids.shape[1]:]
        out = self.processor.batch_decode(
            gen, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return out.strip()
