from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


DEFAULT_MODEL_NAME = "bmd1905/vietnamese-correction-v2"
QUIT_COMMANDS = {":q", ":quit", ":exit"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually test the Vietnamese correction model from Hugging Face."
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Hugging Face model name or a local model directory.",
    )
    parser.add_argument(
        "--text",
        action="append",
        default=[],
        help="Correct a single text value. Repeat the flag to test multiple inputs.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Read test inputs from a UTF-8 text file, one example per line.",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Device to run inference on.",
    )
    parser.add_argument(
        "--max-source-length",
        type=int,
        default=256,
        help="Maximum source token length before truncation.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=256,
        help="Maximum number of generated tokens.",
    )
    parser.add_argument(
        "--num-beams",
        type=int,
        default=1,
        help="Beam size for generation.",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Only load local files and never hit the Hugging Face Hub.",
    )
    return parser.parse_args()


def load_texts(cli_texts: list[str], file_path: Path | None) -> list[str]:
    texts = [text for text in cli_texts if text.strip()]
    if file_path is None:
        return texts

    file_lines = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [*texts, *file_lines]


def format_result(index: int, source: str, corrected: str) -> str:
    return (
        f"[{index}] Input : {source}\n"
        f"[{index}] Output: {corrected}"
    )


class ManualCorrector:
    def __init__(
        self,
        model_name: str,
        *,
        device: str,
        max_source_length: int,
        max_new_tokens: int,
        num_beams: int,
        local_files_only: bool,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.max_source_length = max_source_length
        self.max_new_tokens = max_new_tokens
        self.num_beams = num_beams
        self.local_files_only = local_files_only
        self._device_name = "cpu"
        self._model = None
        self._tokenizer = None

    def load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Thiếu dependency. Hãy chạy `pip install -r requirements.txt` trước."
            ) from exc

        self._device_name = resolve_device(self.device, torch.cuda.is_available())
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            local_files_only=self.local_files_only,
        )
        self._model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            local_files_only=self.local_files_only,
        )
        self._model.to(self._device_name)
        self._model.eval()

    @property
    def device_name(self) -> str:
        return self._device_name

    def correct_many(self, texts: Iterable[str]) -> list[str]:
        self.load()
        assert self._model is not None
        assert self._tokenizer is not None

        text_list = list(texts)
        if not text_list:
            return []

        import torch

        encoded = self._tokenizer(
            text_list,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_source_length,
        )
        encoded = {
            key: value.to(self._device_name)
            for key, value in encoded.items()
        }

        with torch.inference_mode():
            generated = self._model.generate(
                **encoded,
                max_new_tokens=self.max_new_tokens,
                num_beams=self.num_beams,
            )

        return [
            text.strip()
            for text in self._tokenizer.batch_decode(
                generated,
                skip_special_tokens=True,
            )
        ]


def resolve_device(requested: str, cuda_available: bool) -> str:
    if requested == "cpu":
        return "cpu"
    if requested == "cuda":
        if not cuda_available:
            raise RuntimeError("CUDA không khả dụng trên máy này.")
        return "cuda"
    return "cuda" if cuda_available else "cpu"


def run_batch(corrector: ManualCorrector, texts: list[str]) -> int:
    corrected = corrector.correct_many(texts)
    for index, (source, output) in enumerate(zip(texts, corrected), start=1):
        print(format_result(index, source, output))
        print()
    return 0


def run_interactive(corrector: ManualCorrector) -> int:
    print(f"Loading model `{corrector.model_name}`...")
    corrector.load()
    print(f"Model ready on `{corrector.device_name}`.")
    print("Nhap 1 dong van ban de sua. Dung `:quit` de thoat.")

    while True:
        try:
            raw_text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not raw_text:
            continue
        if raw_text.lower() in QUIT_COMMANDS:
            return 0

        corrected = corrector.correct_many([raw_text])[0]
        print(format_result(1, raw_text, corrected))
        print()


def main() -> int:
    args = parse_args()
    texts = load_texts(args.text, args.file)
    corrector = ManualCorrector(
        args.model_name,
        device=args.device,
        max_source_length=args.max_source_length,
        max_new_tokens=args.max_new_tokens,
        num_beams=args.num_beams,
        local_files_only=args.local_files_only,
    )

    if texts:
        return run_batch(corrector, texts)
    return run_interactive(corrector)


if __name__ == "__main__":
    raise SystemExit(main())
