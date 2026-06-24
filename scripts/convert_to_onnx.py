from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a local seq2seq model to ONNX.")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("models") / "bartpho-correction-v2",
        help="Directory containing the original transformers model.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models") / "bartpho-correction-v2-onnx",
        help="Directory where ONNX files will be written.",
    )
    parser.add_argument("--opset", type=int, default=14)
    args = parser.parse_args()

    from optimum.exporters.onnx import main_export

    args.output_dir.mkdir(parents=True, exist_ok=True)
    main_export(
        model_name_or_path=str(args.model_dir),
        output=str(args.output_dir),
        task="text2text-generation-with-past",
        opset=args.opset,
        device="cpu",
    )

    for sidecar in [
        "config.json",
        "generation_config.json",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "sentencepiece.bpe.model",
    ]:
        source = args.model_dir / sidecar
        if source.exists():
            shutil.copy2(source, args.output_dir / sidecar)

    print(f"Exported ONNX model to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
