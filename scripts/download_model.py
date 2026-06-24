from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the base correction model.")
    parser.add_argument(
        "--model-name",
        default="bmd1905/vietnamese-correction-v2",
        help="Hugging Face model name to download.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models") / "bartpho-correction-v2",
        help="Directory where the original tokenizer and weights will be saved.",
    )
    args = parser.parse_args()

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    tokenizer.save_pretrained(args.output_dir)
    model.save_pretrained(args.output_dir)
    print(f"Saved tokenizer and model to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
