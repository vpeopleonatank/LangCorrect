from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from pathlib import Path
from typing import Protocol


class CorrectionAdapter(Protocol):
    def load(self) -> None:
        """Load any model resources needed for correction."""

    def correct(self, text: str) -> str:
        """Return the corrected text for one chunk."""

    def count_tokens(self, text: str) -> int:
        """Return the tokenizer count used for chunking."""


class ModelSetupError(RuntimeError):
    """Model artifacts are missing or inconsistent."""


class ModelRuntimeError(RuntimeError):
    """Inference failed or cannot start."""


@dataclass(frozen=True)
class ModelArtifactPaths:
    root: Path
    encoder: Path
    decoder: Path
    decoder_with_past: Path
    sentencepiece_model: Path
    monolingual_vocab: Path

    @classmethod
    def from_dir(cls, model_dir: Path) -> "ModelArtifactPaths":
        encoder = model_dir / "encoder_model.onnx"
        decoder = model_dir / "decoder_model.onnx"
        decoder_with_past = model_dir / "decoder_with_past_model.onnx"
        sentencepiece_model = model_dir / "sentencepiece.bpe.model"
        monolingual_vocab = model_dir / "dict.txt"
        required = [
            encoder,
            decoder,
            decoder_with_past,
            model_dir / "config.json",
            model_dir / "tokenizer_config.json",
            sentencepiece_model,
            monolingual_vocab,
        ]
        missing = [path.name for path in required if not path.exists()]
        if missing:
            joined = ", ".join(missing)
            raise ModelSetupError(
                "Thiếu artifact model offline/tokenizer tại "
                f"`{model_dir}` ({joined}). "
                "Hãy chạy scripts/download_model.py, scripts/convert_to_onnx.py và "
                "scripts/quantize_model.py hoặc đặt `VICORRECT_MODEL_DIR` trỏ tới artifact đã chuẩn bị."
            )
        return cls(
            root=model_dir,
            encoder=encoder,
            decoder=decoder,
            decoder_with_past=decoder_with_past,
            sentencepiece_model=sentencepiece_model,
            monolingual_vocab=monolingual_vocab,
        )


def _load_local_tokenizer(
    artifacts: ModelArtifactPaths,
    *,
    auto_tokenizer_cls=None,
    bartpho_tokenizer_cls=None,
):
    if auto_tokenizer_cls is None or bartpho_tokenizer_cls is None:
        from transformers import AutoTokenizer, BartphoTokenizer

        auto_tokenizer_cls = AutoTokenizer
        bartpho_tokenizer_cls = BartphoTokenizer

    try:
        return auto_tokenizer_cls.from_pretrained(
            artifacts.root,
            local_files_only=True,
        )
    except TypeError as exc:
        # BartPho artifacts sometimes omit enough metadata for AutoTokenizer to
        # infer the reduced Vietnamese vocabulary path even though the files are present.
        if "NoneType" not in str(exc):
            raise
        return bartpho_tokenizer_cls(
            vocab_file=str(artifacts.sentencepiece_model),
            monolingual_vocab_file=str(artifacts.monolingual_vocab),
        )


class OfflineCorrectionAdapter:
    """Load a local ONNX seq2seq model without touching the network."""

    def __init__(self, model_dir: Path, device: str = "cpu") -> None:
        self.model_dir = model_dir
        self.device = device
        self._tokenizer = None
        self._model = None
        self._logger = logging.getLogger(__name__)

    def load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        artifacts = ModelArtifactPaths.from_dir(self.model_dir)
        provider = self._resolve_provider(self.device)
        try:
            from optimum.onnxruntime import ORTModelForSeq2SeqLM
        except ImportError as exc:
            raise ModelRuntimeError(
                "Thiếu thư viện runtime. Hãy cài dependencies bằng `pip install -r requirements.txt`."
            ) from exc

        try:
            self._tokenizer = _load_local_tokenizer(artifacts)
            self._model = ORTModelForSeq2SeqLM.from_pretrained(
                artifacts.root,
                provider=provider,
                local_files_only=True,
            )
        except Exception as exc:  # pragma: no cover - depends on optional runtime
            self._logger.exception("Unable to load offline model")
            raise ModelRuntimeError(
                "Không tải được model offline. Kiểm tra tokenizer/ONNX artifact và log tại logs/vicorrect.log."
            ) from exc

    def count_tokens(self, text: str) -> int:
        self.load()
        assert self._tokenizer is not None
        return len(self._tokenizer.encode(text, add_special_tokens=False))

    def correct(self, text: str) -> str:
        self.load()
        assert self._tokenizer is not None
        assert self._model is not None
        try:
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
            )
            output_tokens = self._model.generate(
                **inputs,
                max_new_tokens=256,
                num_beams=1,
            )
            return self._tokenizer.decode(
                output_tokens[0],
                skip_special_tokens=True,
            ).strip()
        except Exception as exc:  # pragma: no cover - depends on optional runtime
            self._logger.exception("Inference failed")
            raise ModelRuntimeError(
                "Model đã được tải nhưng suy luận thất bại. Xem log để biết chi tiết và thử lại với artifact hợp lệ."
            ) from exc

    def _resolve_provider(self, device: str) -> str:
        normalized = device.lower()
        if normalized in {"auto", "gpu"}:
            return "CUDAExecutionProvider"
        return "CPUExecutionProvider"


def default_model_dir() -> Path:
    configured = os.environ.get("VICORRECT_MODEL_DIR")
    if configured:
        return Path(configured)
    repo_root = Path(__file__).resolve().parents[2]
    default_dir = repo_root / "models"
    candidates = [
        default_dir / "bartpho-correction-v2-onnx",
        default_dir / "bartpho-correction-v2-onnx-int8",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def build_default_adapter(device: str = "cpu") -> OfflineCorrectionAdapter:
    return OfflineCorrectionAdapter(default_model_dir(), device=device)
