from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantize exported ONNX files to INT8.")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("models") / "bartpho-correction-v2-onnx",
        help="Directory containing exported ONNX files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models") / "bartpho-correction-v2-onnx-int8",
        help="Directory where quantized ONNX files will be written.",
    )
    args = parser.parse_args()

    from onnxruntime.quantization import QuantType, quantize_dynamic

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename in [
        "encoder_model.onnx",
        "decoder_model.onnx",
        "decoder_with_past_model.onnx",
    ]:
        quantize_dynamic(
            model_input=str(args.model_dir / filename),
            model_output=str(args.output_dir / filename),
            weight_type=QuantType.QInt8,
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
            target = args.output_dir / sidecar
            target.write_bytes(source.read_bytes())

    print(f"Quantized ONNX model to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
