# PRD: ViCorrect — Ứng dụng sửa lỗi chính tả tiếng Việt cho Windows

**Version:** 1.0
**Ngày tạo:** 2026-06-23
**Trạng thái:** Draft → Ready for Implementation

---

## 1. Tổng quan sản phẩm

### 1.1 Vấn đề cần giải quyết

Hiện tại trên Windows chỉ có các công cụ sửa lỗi chính tả tiếng Việt dạng rule-based / dictionary-based (Tummo Spell, VCatSpell, VietSpell). Các công cụ này:
- Không hiểu ngữ cảnh → sửa sai khi từ đúng nhưng không phù hợp ngữ cảnh
- Không xử lý được lỗi dính chữ phức tạp, teencode, thiếu dấu
- Không có khả năng học hỏi từ dữ liệu

Trong khi đó, đã có các model AI (BARTpho fine-tuned) trên HuggingFace đạt chất lượng rất cao nhưng chưa ai đóng gói thành ứng dụng desktop cho người dùng cuối.

### 1.2 Giải pháp

Xây dựng **ViCorrect** — ứng dụng desktop Windows chạy hoàn toàn offline, sử dụng model AI (BARTpho-syllable fine-tuned, convert sang ONNX) để sửa lỗi chính tả tiếng Việt. Ứng dụng nhắm tới người dùng phổ thông (nhân viên văn phòng, sinh viên) và phải chạy được trên cả máy yếu (4-8GB RAM, không GPU) lẫn máy có GPU.

### 1.3 Phạm vi

- **Phase 1 (MVP):** App standalone — paste text vào, sửa lỗi, export
- **Phase 2:** Thêm LLM option (Ollama) cho máy có GPU
- **Phase 3:** Plugin Word/Excel

**Tài liệu này tập trung vào Phase 1.**

---

## 2. Đối tượng người dùng

### 2.1 Primary Persona: Nhân viên văn phòng

- Soạn thảo văn bản hàng ngày (email, báo cáo, công văn)
- Không có kiến thức kỹ thuật
- Máy tính công ty, thường 8GB RAM, không GPU
- Cần: cài đặt đơn giản (1 click), giao diện tiếng Việt, chạy nhanh

### 2.2 Secondary Persona: Sinh viên / Content writer

- Viết bài luận, blog post, nội dung mạng xã hội
- Có thể viết teencode / thiếu dấu rồi cần chuẩn hóa
- Máy tính cá nhân, cấu hình đa dạng
- Cần: xử lý teencode, batch processing nhiều file

---

## 3. Phân tích & lựa chọn Model

### 3.1 So sánh 3 model ứng viên

| Tiêu chí | bmd1905/vietnamese-correction-v2 | yammdd/vietnamese-error-correction | MinhDucNguyen9705/vietnamese-correction-2.0 |
|---|---|---|---|
| Base model | vinai/bartpho-syllable | vinai/bartpho-syllable + LoRA | vinai/bartpho-syllable |
| Params | ~396M (full fine-tune) | ~396M base + LoRA adapter | ~396M (full fine-tune) |
| License | Apache 2.0 | MIT | MIT |
| Training data | VNTC dataset (customized) | ~70K câu từ social media | Unknown |
| Đánh giá | Được trích dẫn trong paper, cộng đồng lớn (54★ GitHub) | BLEU 86.34, Word Acc 93.28%, CER 3.60% | Không có metrics |
| Teencode | Hạn chế | Tốt ("zui wa" → "vui quá") | Không rõ |
| Documentation | Tốt, có ví dụ | Rất chi tiết, có eval theo độ dài | Minimal ("More info needed") |
| Downloads/tháng | Cao nhất trong 3 | Vừa | 1,611 |

### 3.2 Quyết định

**Model chính: `bmd1905/vietnamese-correction-v2`**
- Lý do: battle-tested nhất, cộng đồng sử dụng lớn nhất, được trích dẫn trong paper học thuật, full fine-tune cho hiệu quả ổn định nhất
- Sử dụng qua pipeline `text2text-generation`

**Model phụ (optional, user có thể chọn): `yammdd/vietnamese-error-correction`**
- Lý do: hỗ trợ teencode tốt hơn, LoRA adapter nhẹ hơn, có evaluation chi tiết
- Phù hợp cho user viết content mạng xã hội

### 3.3 LLM Option (Phase 2)

Cho máy có GPU rời (RTX series), tích hợp thêm:
- Gọi Ollama local API với model Qwen2.5-3B-Instruct hoặc Gemma-3-4B
- Prompt template chuyên biệt cho sửa lỗi chính tả tiếng Việt
- Lợi ích: sửa được cả ngữ pháp, ngữ nghĩa, phong cách viết
- Trade-off: chậm hơn (1-5s/câu), cần 4-6GB VRAM

---

## 4. Kiến trúc kỹ thuật

### 4.1 Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────┐
│  UI Layer (PyQt6)                                   │
│  ┌──────────┐ ┌───────────┐ ┌────────┐ ┌────────┐  │
│  │Text      │ │Diff       │ │Settings│ │Export  │  │
│  │Editor    │ │Viewer     │ │Panel   │ │Module  │  │
│  └──────────┘ └───────────┘ └────────┘ └────────┘  │
├─────────────────────────────────────────────────────┤
│  Backend Engine (Python)                            │
│  ┌──────────┐ ┌───────────┐ ┌──────────────────┐   │
│  │Preprocess│→│Inference  │→│Postprocess       │   │
│  │(tách câu)│ │(ONNX RT)  │ │(diff, highlight) │   │
│  └──────────┘ └───────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────┤
│  Model Layer                                        │
│  ┌────────────────────┐  ┌────────────────────────┐ │
│  │BARTpho ONNX (INT8) │  │LLM via Ollama (Opt.)  │ │
│  │~400MB, CPU ready   │  │GPU only, Phase 2      │ │
│  └────────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 4.2 Tech Stack

| Component | Technology | Lý do chọn |
|---|---|---|
| Language | Python 3.10+ | Ecosystem ML tốt nhất, HuggingFace native |
| UI Framework | PyQt6 | Native look trên Windows, hiệu năng tốt, ko cần web runtime |
| Inference | ONNX Runtime | Nhanh hơn PyTorch 2-3x trên CPU, tự động detect GPU, nhẹ |
| Model format | ONNX (INT8 quantized) | Giảm từ ~1.6GB → ~400MB, inference nhanh hơn trên CPU |
| Tokenizer | transformers (AutoTokenizer) | Cần giữ tokenizer gốc của BARTpho |
| Text processing | underthesea hoặc regex | Tách câu tiếng Việt |
| Diff engine | difflib (stdlib) | So sánh input vs output, tạo highlight |
| Packaging | PyInstaller + Inno Setup | Tạo single .exe installer cho Windows |
| Auto-update | (Phase 2) | Có thể dùng pyupdater hoặc custom |

### 4.3 Cấu trúc thư mục Project

```
vicorrect/
├── README.md
├── requirements.txt
├── setup.py
├── pyproject.toml
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   │
│   ├── ui/                        # UI Layer
│   │   ├── __init__.py
│   │   ├── main_window.py         # Cửa sổ chính
│   │   ├── text_editor.py         # Widget nhập/hiển thị text
│   │   ├── diff_viewer.py         # Widget hiển thị diff (highlight)
│   │   ├── settings_dialog.py     # Dialog cài đặt
│   │   ├── about_dialog.py        # Dialog giới thiệu
│   │   ├── styles.py              # QSS stylesheets
│   │   └── resources/             # Icons, fonts
│   │       ├── icon.ico
│   │       ├── icon.png
│   │       └── styles.qss
│   │
│   ├── engine/                    # Backend Engine
│   │   ├── __init__.py
│   │   ├── preprocessor.py        # Tách câu, chuẩn hóa input
│   │   ├── inference.py           # ONNX Runtime inference wrapper
│   │   ├── postprocessor.py       # Diff engine, merge kết quả
│   │   ├── model_manager.py       # Load/unload model, detect hardware
│   │   └── batch_processor.py     # Xử lý file batch (TXT, DOCX)
│   │
│   ├── models/                    # Model files (shipped with app)
│   │   ├── README.md
│   │   └── .gitkeep               # Model files too large for git
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py              # App configuration (QSettings)
│       ├── logger.py              # Logging setup
│       ├── hardware_detect.py     # Detect GPU, RAM, recommend settings
│       └── file_handler.py        # Read/write TXT, DOCX files
│
├── scripts/
│   ├── convert_to_onnx.py         # Script convert PyTorch → ONNX
│   ├── quantize_model.py          # Script quantize ONNX FP32 → INT8
│   ├── benchmark.py               # Benchmark inference speed
│   └── download_model.py          # Download model từ HuggingFace
│
├── installer/
│   ├── vicorrect.iss              # Inno Setup script
│   ├── build_exe.py               # PyInstaller build script
│   └── assets/                    # Installer assets (license, banner)
│
├── tests/
│   ├── test_preprocessor.py
│   ├── test_inference.py
│   ├── test_postprocessor.py
│   ├── test_accuracy.py           # Test với bộ câu mẫu
│   └── test_data/
│       └── sample_texts.json      # Bộ test câu mẫu
│
└── docs/
    ├── USER_GUIDE.md              # Hướng dẫn sử dụng
    └── DEVELOPER.md               # Hướng dẫn phát triển
```

---

## 5. Yêu cầu chức năng (Functional Requirements)

### 5.1 [F01] Nhập văn bản

- **F01.1:** Người dùng có thể paste văn bản vào text editor
- **F01.2:** Người dùng có thể gõ trực tiếp vào text editor
- **F01.3:** Người dùng có thể mở file TXT hoặc DOCX để import nội dung
- **F01.4:** Người dùng có thể kéo thả file vào cửa sổ app (drag & drop)
- **F01.5:** Hiển thị số từ và số ký tự ở status bar

### 5.2 [F02] Sửa lỗi chính tả

- **F02.1:** Nút "Sửa lỗi" (hoặc Ctrl+Enter) gửi toàn bộ văn bản đi xử lý
- **F02.2:** Văn bản được tách thành từng câu (max 256 tokens/câu) trước khi gửi vào model
- **F02.3:** Hiển thị progress bar trong khi xử lý (X/Y câu đã hoàn thành)
- **F02.4:** Kết quả hiển thị ở panel bên phải (split view: original | corrected)
- **F02.5:** Xử lý trong background thread (QThread) để UI không bị đơ
- **F02.6:** Có nút Cancel để hủy giữa chừng

### 5.3 [F03] Review thay đổi

- **F03.1:** Hiển thị diff view — highlight các từ/cụm từ đã thay đổi
  - Màu đỏ nhạt (background): phần bị xóa/thay thế trong bản gốc
  - Màu xanh nhạt (background): phần mới trong bản đã sửa
- **F03.2:** Người dùng click vào mỗi thay đổi để Accept hoặc Reject
- **F03.3:** Nút "Accept All" để chấp nhận tất cả
- **F03.4:** Nút "Reject All" để hủy tất cả thay đổi
- **F03.5:** Counter hiển thị: "X/Y thay đổi đã review"
- **F03.6:** Keyboard navigation: Tab để đi đến thay đổi tiếp theo, Enter để Accept, Delete để Reject

### 5.4 [F04] Export kết quả

- **F04.1:** Copy kết quả vào clipboard (nút Copy hoặc Ctrl+C trên panel kết quả)
- **F04.2:** Lưu thành file TXT (UTF-8)
- **F04.3:** Lưu thành file DOCX (giữ format cơ bản)
- **F04.4:** "Replace original" — ghi đè file gốc nếu import từ file

### 5.5 [F05] Cài đặt / Settings

- **F05.1:** Chọn model sử dụng:
  - `bmd1905/vietnamese-correction-v2` (mặc định)
  - `yammdd/vietnamese-error-correction` (optional, cần download thêm)
- **F05.2:** Chọn device: Auto (khuyến nghị) / CPU / GPU
- **F05.3:** Max length per sentence (mặc định 256 tokens)
- **F05.4:** Batch size (mặc định 1, có thể tăng nếu có GPU)
- **F05.5:** Theme: Light / Dark / System (theo Windows)
- **F05.6:** Ngôn ngữ giao diện: Tiếng Việt (mặc định) / English
- **F05.7:** Font size cho text editor (adjustable)

### 5.6 [F06] Batch Processing

- **F06.1:** Tab "Batch" cho phép chọn nhiều file TXT/DOCX cùng lúc
- **F06.2:** Hiển thị danh sách file với trạng thái (Pending / Processing / Done / Error)
- **F06.3:** Xử lý lần lượt từng file
- **F06.4:** Lưu kết quả cùng thư mục, thêm suffix "_corrected"
- **F06.5:** Tạo report tổng hợp: bao nhiêu file, bao nhiêu lỗi đã sửa

---

## 6. Yêu cầu phi chức năng (Non-Functional Requirements)

### 6.1 Hiệu năng

| Metric | Target (CPU, 8GB RAM) | Target (GPU, RTX 3060+) |
|---|---|---|
| Thời gian khởi động app | < 5 giây | < 3 giây |
| Thời gian load model lần đầu | < 10 giây | < 5 giây |
| Inference 1 câu (≤30 từ) | < 500ms | < 100ms |
| Inference 1 câu (≤100 từ) | < 1500ms | < 300ms |
| Xử lý 1 trang A4 (~300 từ) | < 15 giây | < 3 giây |
| RAM sử dụng (idle) | < 500MB | < 500MB |
| RAM sử dụng (processing) | < 2GB | < 2GB |
| VRAM sử dụng | N/A | < 2GB |

### 6.2 Kích thước cài đặt

| Component | Kích thước ước tính |
|---|---|
| App (Python + PyQt6 bundled) | ~80-120MB |
| Model ONNX INT8 | ~400MB |
| Tokenizer files | ~5MB |
| ONNX Runtime (CPU) | ~30MB |
| ONNX Runtime (GPU, optional) | ~50MB |
| **Tổng installer** | **~550-650MB** |

### 6.3 Tương thích

- Windows 10 (64-bit) trở lên
- Windows 11
- RAM tối thiểu: 4GB (khuyến nghị 8GB)
- Disk trống: 1.5GB
- Không yêu cầu internet sau khi cài đặt
- Không yêu cầu Python được cài sẵn (bundled)

### 6.4 Bảo mật & Quyền riêng tư

- Toàn bộ xử lý offline, không gửi dữ liệu ra internet
- Không thu thập bất kỳ thông tin người dùng nào
- Không yêu cầu quyền admin để cài đặt (cài vào %LOCALAPPDATA%)
- Văn bản chỉ được giữ trong RAM, không lưu vào temp file

### 6.5 UX / Accessibility

- Giao diện tiếng Việt là mặc định
- Hỗ trợ keyboard shortcuts cho mọi tác vụ chính
- Font size adjustable (12-24px)
- Tương thích Windows High Contrast mode
- Status bar luôn hiển thị trạng thái hiện tại (Ready / Processing / Done)

---

## 7. Chi tiết Implementation

### 7.1 Model Conversion Pipeline

**Bước 1: Download model từ HuggingFace**

```python
# scripts/download_model.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "bmd1905/vietnamese-correction-v2"
save_dir = "./models/bartpho-correction-v2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

tokenizer.save_pretrained(save_dir)
model.save_pretrained(save_dir)
```

**Bước 2: Convert sang ONNX**

```python
# scripts/convert_to_onnx.py
from optimum.exporters.onnx import main_export

main_export(
    model_name_or_path="./models/bartpho-correction-v2",
    output="./models/bartpho-correction-v2-onnx",
    task="text2text-generation-with-past",  # Seq2Seq with KV cache
    opset=14,
    device="cpu",
)
```

Lưu ý quan trọng: BARTpho là encoder-decoder (MBart architecture), khi export ONNX sẽ tạo ra:
- `encoder_model.onnx` — encode input
- `decoder_model.onnx` — decode từng token (with past key values)
- `decoder_with_past_model.onnx` — decode nhanh hơn nhờ KV cache

**Bước 3: Quantize INT8**

```python
# scripts/quantize_model.py
from onnxruntime.quantization import quantize_dynamic, QuantType

for model_file in ["encoder_model.onnx", "decoder_model.onnx", "decoder_with_past_model.onnx"]:
    input_path = f"./models/bartpho-correction-v2-onnx/{model_file}"
    output_path = f"./models/bartpho-correction-v2-onnx-int8/{model_file}"

    quantize_dynamic(
        model_input=input_path,
        model_output=output_path,
        weight_type=QuantType.QInt8,
    )
```

**Thư viện cần thiết cho conversion:**
```
pip install transformers optimum onnx onnxruntime
```

### 7.2 Inference Engine

```python
# src/engine/inference.py
"""
ONNX Runtime inference wrapper cho BARTpho Seq2Seq model.

Sử dụng optimum ORTModelForSeq2SeqLM để load ONNX model,
tự động handle encoder + decoder + KV cache.
"""

import os
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from transformers import AutoTokenizer


class CorrectionEngine:
    """
    Engine sửa lỗi chính tả tiếng Việt.

    Hỗ trợ:
    - CPU inference (mặc định, dùng INT8 quantized)
    - GPU inference (nếu có CUDA-capable GPU)
    - Tự động detect hardware và chọn provider phù hợp
    """

    def __init__(self, model_dir: str, device: str = "auto"):
        """
        Args:
            model_dir: Đường dẫn tới thư mục chứa ONNX model + tokenizer
            device: "auto" | "cpu" | "gpu"
        """
        self.model_dir = model_dir
        self.device = device
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load(self):
        """Load model và tokenizer vào memory."""
        provider = self._detect_provider()

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = ORTModelForSeq2SeqLM.from_pretrained(
            self.model_dir,
            provider=provider,
        )
        self._loaded = True

    def unload(self):
        """Giải phóng memory."""
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def correct(self, text: str, max_length: int = 512) -> str:
        """
        Sửa lỗi chính tả cho 1 câu/đoạn văn bản.

        Args:
            text: Văn bản cần sửa (nên ≤ 256 tokens)
            max_length: Chiều dài tối đa output

        Returns:
            Văn bản đã được sửa lỗi
        """
        if not self._loaded:
            raise RuntimeError("Model chưa được load. Gọi .load() trước.")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
            padding=True,
        )

        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=5,           # Beam search cho chất lượng tốt hơn
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

        corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected.strip()

    def correct_batch(self, texts: list[str], max_length: int = 512) -> list[str]:
        """Sửa lỗi cho nhiều câu cùng lúc."""
        results = []
        for text in texts:
            results.append(self.correct(text, max_length))
        return results

    def _detect_provider(self) -> str:
        """Tự động detect hardware và chọn ONNX execution provider."""
        if self.device == "cpu":
            return "CPUExecutionProvider"
        elif self.device == "gpu":
            return "CUDAExecutionProvider"
        else:  # auto
            try:
                import onnxruntime
                available = onnxruntime.get_available_providers()
                if "CUDAExecutionProvider" in available:
                    return "CUDAExecutionProvider"
            except Exception:
                pass
            return "CPUExecutionProvider"
```

### 7.3 Preprocessor

```python
# src/engine/preprocessor.py
"""
Tách văn bản thành từng câu để gửi vào model.

BARTpho có giới hạn 1024 tokens nhưng hiệu quả tốt nhất ở ≤256 tokens.
Cần tách văn bản dài thành từng câu/đoạn ngắn trước khi inference.
"""

import re


class Preprocessor:
    """Tiền xử lý văn bản tiếng Việt trước khi gửi vào model."""

    # Regex tách câu tiếng Việt (dấu chấm, chấm hỏi, chấm than + xuống dòng)
    SENTENCE_SPLITTER = re.compile(
        r'(?<=[.!?])\s+|(?<=\n)\s*'
    )

    # Ký tự cần chuẩn hóa
    NORMALIZE_MAP = {
        '\u00a0': ' ',      # Non-breaking space → space
        '\u200b': '',        # Zero-width space → remove
        '\u200c': '',        # Zero-width non-joiner → remove
        '\ufeff': '',        # BOM → remove
        '"': '"',            # Smart quotes → standard
        '"': '"',
        '\u2018': "'",       # Smart single quotes
        '\u2019': "'",
        '…': '...',          # Ellipsis character → 3 dots
    }

    def __init__(self, max_tokens: int = 256):
        self.max_tokens = max_tokens

    def process(self, text: str) -> list[str]:
        """
        Tách văn bản thành danh sách câu, mỗi câu ≤ max_tokens.

        Args:
            text: Văn bản gốc

        Returns:
            Danh sách các câu đã chuẩn hóa
        """
        text = self._normalize(text)
        sentences = self._split_sentences(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _normalize(self, text: str) -> str:
        """Chuẩn hóa ký tự đặc biệt."""
        for old, new in self.NORMALIZE_MAP.items():
            text = text.replace(old, new)
        # Chuẩn hóa multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        # Chuẩn hóa multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def _split_sentences(self, text: str) -> list[str]:
        """
        Tách câu thông minh cho tiếng Việt.
        Giữ nguyên cấu trúc đoạn (paragraph).
        """
        paragraphs = text.split('\n')
        sentences = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Tách câu trong paragraph
            parts = self.SENTENCE_SPLITTER.split(para)
            current = ""

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                # Ước lượng token count (1 từ tiếng Việt ≈ 2-3 syllable tokens)
                estimated_tokens = len(part.split()) * 2.5

                if estimated_tokens > self.max_tokens:
                    # Câu quá dài, cần tách thêm theo dấu phẩy
                    sub_parts = self._split_long_sentence(part)
                    sentences.extend(sub_parts)
                else:
                    sentences.append(part)

        return sentences

    def _split_long_sentence(self, sentence: str) -> list[str]:
        """Tách câu dài theo dấu phẩy hoặc dấu chấm phẩy."""
        parts = re.split(r'(?<=[,;])\s+', sentence)
        result = []
        current = ""

        for part in parts:
            if current:
                combined = current + ", " + part
                if len(combined.split()) * 2.5 <= self.max_tokens:
                    current = combined
                else:
                    result.append(current)
                    current = part
            else:
                current = part

        if current:
            result.append(current)

        return result
```

### 7.4 Postprocessor (Diff Engine)

```python
# src/engine/postprocessor.py
"""
So sánh văn bản gốc và văn bản đã sửa,
tạo diff để hiển thị cho người dùng review.
"""

import difflib
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    UNCHANGED = "unchanged"
    ADDED = "added"
    REMOVED = "removed"
    REPLACED = "replaced"


@dataclass
class TextChange:
    """Một thay đổi trong văn bản."""
    change_type: ChangeType
    original: str           # Text gốc (empty nếu ADDED)
    corrected: str          # Text đã sửa (empty nếu REMOVED)
    position: int           # Vị trí ký tự trong văn bản gốc
    sentence_index: int     # Câu thứ mấy
    accepted: bool = False  # User đã accept chưa


class Postprocessor:
    """Tạo diff giữa văn bản gốc và văn bản đã sửa."""

    def create_diff(
        self,
        original_sentences: list[str],
        corrected_sentences: list[str],
    ) -> list[TextChange]:
        """
        So sánh từng cặp câu gốc-sửa, trả về danh sách changes.

        Args:
            original_sentences: Danh sách câu gốc
            corrected_sentences: Danh sách câu đã sửa

        Returns:
            Danh sách TextChange để hiển thị trong UI
        """
        changes = []
        char_offset = 0

        for i, (orig, corr) in enumerate(zip(original_sentences, corrected_sentences)):
            if orig.strip() == corr.strip():
                char_offset += len(orig) + 1  # +1 cho space/newline
                continue

            # Word-level diff
            orig_words = orig.split()
            corr_words = corr.split()

            matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
            word_offset = 0

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    word_offset += sum(len(w) + 1 for w in orig_words[i1:i2])
                elif tag == 'replace':
                    orig_text = ' '.join(orig_words[i1:i2])
                    corr_text = ' '.join(corr_words[j1:j2])
                    changes.append(TextChange(
                        change_type=ChangeType.REPLACED,
                        original=orig_text,
                        corrected=corr_text,
                        position=char_offset + word_offset,
                        sentence_index=i,
                    ))
                    word_offset += len(orig_text) + 1
                elif tag == 'insert':
                    corr_text = ' '.join(corr_words[j1:j2])
                    changes.append(TextChange(
                        change_type=ChangeType.ADDED,
                        original="",
                        corrected=corr_text,
                        position=char_offset + word_offset,
                        sentence_index=i,
                    ))
                elif tag == 'delete':
                    orig_text = ' '.join(orig_words[i1:i2])
                    changes.append(TextChange(
                        change_type=ChangeType.REMOVED,
                        original=orig_text,
                        corrected="",
                        position=char_offset + word_offset,
                        sentence_index=i,
                    ))
                    word_offset += len(orig_text) + 1

            char_offset += len(orig) + 1

        return changes

    def apply_changes(
        self,
        original_sentences: list[str],
        corrected_sentences: list[str],
        changes: list[TextChange],
    ) -> str:
        """
        Áp dụng các changes đã được accept vào văn bản gốc.

        Returns:
            Văn bản cuối cùng sau khi áp dụng accepted changes
        """
        result_sentences = []

        for i, (orig, corr) in enumerate(zip(original_sentences, corrected_sentences)):
            # Check xem tất cả changes của câu này đã accept hết chưa
            sentence_changes = [c for c in changes if c.sentence_index == i]

            if not sentence_changes:
                # Không có thay đổi → giữ nguyên
                result_sentences.append(orig)
            elif all(c.accepted for c in sentence_changes):
                # Tất cả accepted → dùng bản sửa
                result_sentences.append(corr)
            elif not any(c.accepted for c in sentence_changes):
                # Không accept cái nào → giữ nguyên
                result_sentences.append(orig)
            else:
                # Mix: cần apply từng change riêng lẻ
                result_sentences.append(
                    self._apply_partial_changes(orig, corr, sentence_changes)
                )

        return ' '.join(result_sentences)

    def _apply_partial_changes(
        self,
        original: str,
        corrected: str,
        changes: list[TextChange],
    ) -> str:
        """Apply từng change riêng lẻ khi user chỉ accept một số."""
        orig_words = original.split()
        corr_words = corrected.split()

        matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
        result_words = []
        change_idx = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                result_words.extend(orig_words[i1:i2])
            elif tag in ('replace', 'insert', 'delete'):
                if change_idx < len(changes) and changes[change_idx].accepted:
                    result_words.extend(corr_words[j1:j2])
                else:
                    result_words.extend(orig_words[i1:i2])
                change_idx += 1

        return ' '.join(result_words)
```

### 7.5 Main Window UI

```python
# src/ui/main_window.py
"""
Cửa sổ chính của ViCorrect.

Layout:
┌─────────────────────────────────────────────┐
│  Menu bar (File | Edit | Settings | Help)   │
├──────────────────────┬──────────────────────┤
│  Original Text       │  Corrected Text      │
│  (editable)          │  (with diff highlight)│
│                      │                      │
│                      │                      │
├──────────────────────┴──────────────────────┤
│  [Sửa lỗi]  [Accept All]  [Reject All]     │
│  [Copy]      [Export TXT]  [Export DOCX]    │
├─────────────────────────────────────────────┤
│  Status: Ready | 150 từ | Model: BARTpho   │
└─────────────────────────────────────────────┘

Lưu ý khi implement:
- Dùng QSplitter cho 2 panel text (có thể resize)
- QPlainTextEdit cho text editor (hiệu năng tốt hơn QTextEdit cho text thuần)
- QTextBrowser hoặc custom QTextEdit cho diff viewer (cần rich text highlighting)
- QThread cho inference (không block UI)
- QProgressBar hiển thị tiến trình xử lý
- QStatusBar hiển thị thông tin (word count, model name, device)
- QSettings lưu cài đặt người dùng (window size, position, preferences)
- App icon .ico (256x256)
- Minimum window size: 800x500
"""
```

### 7.6 UI Styling

```
# src/ui/resources/styles.qss

Nguyên tắc thiết kế:
- Clean, modern, flat design
- 2 theme: Light (mặc định) và Dark
- Font: Segoe UI (Windows system font) hoặc fallback sans-serif
- Palette:
  - Primary: #2563EB (blue-600)
  - Success (accepted change): #16A34A (green-600) background #DCFCE7
  - Danger (removed text): #DC2626 (red-600) background #FEE2E2
  - Warning (pending change): #F59E0B (amber-500) background #FEF3C7
  - Neutral surface: #F8FAFC (slate-50)
  - Border: #E2E8F0 (slate-200)
- Border radius: 6px cho buttons, 8px cho panels
- Spacing: 8px base unit
- Diff highlighting:
  - Added text: background #DCFCE7, text #166534
  - Removed text: background #FEE2E2, text #991B1B, strikethrough
  - Changed text: background #FEF3C7, text #92400E
```

---

## 8. Luồng xử lý chi tiết (Data Flow)

### 8.1 Luồng chính: Sửa lỗi văn bản

```
1. User paste/gõ văn bản vào panel trái
2. User nhấn "Sửa lỗi" (hoặc Ctrl+Enter)
3. UI disable nút, hiện progress bar
4. [Main Thread] → emit signal tới QThread
5. [Worker Thread]:
   a. Preprocessor.process(text) → list[str] sentences
   b. Với mỗi sentence:
      - engine.correct(sentence) → corrected_sentence
      - emit progress signal (i/total)
   c. Postprocessor.create_diff(originals, correcteds) → list[TextChange]
   d. emit result signal(changes)
6. [Main Thread] nhận result signal:
   a. Hiển thị corrected text ở panel phải
   b. Highlight diff ở cả 2 panel
   c. Enable các nút Accept/Reject
   d. Ẩn progress bar
   e. Update status bar: "Tìm thấy X lỗi"
```

### 8.2 Luồng Accept/Reject

```
1. User click vào 1 highlighted change
2. Popup nhỏ hiện: [Accept ✓] [Reject ✗]
   Hoặc: click trái = Accept, click phải = Reject
3. Update TextChange.accepted
4. Re-render diff view (accepted → green, rejected → dimmed)
5. Update counter: "X/Y thay đổi đã review"
6. Khi tất cả đã review → enable Export buttons
```

### 8.3 Luồng Export

```
1. User chọn Export (TXT / DOCX / Copy)
2. Postprocessor.apply_changes() → final text
3. Tùy loại export:
   - Copy: QApplication.clipboard().setText(final_text)
   - TXT: QFileDialog → write UTF-8 file
   - DOCX: python-docx → create document → save
4. Status bar: "Đã lưu file abc.txt"
```

---

## 9. Đóng gói & Phân phối

### 9.1 PyInstaller Build

```python
# installer/build_exe.py
"""
Script build .exe bằng PyInstaller.

Chạy: python installer/build_exe.py

Output: dist/ViCorrect/ViCorrect.exe
"""

# PyInstaller spec key points:
# - onedir mode (không dùng onefile vì model ~400MB)
# - Include model files trong datas
# - Include ONNX Runtime DLLs
# - Include PyQt6 plugins
# - UPX compression cho các file nhỏ
# - Icon: src/ui/resources/icon.ico
# - Console=False (GUI app)
# - Version info embedded

# Approximate command:
# pyinstaller --name ViCorrect \
#   --windowed \
#   --icon=src/ui/resources/icon.ico \
#   --add-data "src/models;models" \
#   --add-data "src/ui/resources;ui/resources" \
#   --hidden-import onnxruntime \
#   --hidden-import PyQt6.QtSvg \
#   src/main.py
```

### 9.2 Inno Setup Installer

```
; installer/vicorrect.iss
; Key configuration:
; - AppName: ViCorrect
; - AppVersion: 1.0.0
; - DefaultDirName: {localappdata}\ViCorrect  (không cần admin)
; - Output: ViCorrect_Setup_1.0.0.exe
; - Compression: lzma2/ultra64
; - Tạo Desktop shortcut
; - Tạo Start Menu entry
; - Uninstaller included
; - Ước tính size after install: ~800MB
; - Supported OS: Windows 10+
```

### 9.3 Cấu trúc thư mục sau cài đặt

```
%LOCALAPPDATA%/ViCorrect/
├── ViCorrect.exe
├── python3.dll (bundled runtime)
├── _internal/                # PyInstaller internals
│   ├── onnxruntime/
│   ├── PyQt6/
│   └── ...
├── models/
│   ├── bartpho-correction-v2-onnx-int8/
│   │   ├── encoder_model.onnx
│   │   ├── decoder_model.onnx
│   │   ├── decoder_with_past_model.onnx
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   ├── special_tokens_map.json
│   │   └── sentencepiece.bpe.model
│   └── (optional) yammdd-error-correction-onnx-int8/
├── config/
│   └── settings.ini
└── logs/
    └── vicorrect.log
```

---

## 10. Test Plan

### 10.1 Bộ test câu mẫu (sample_texts.json)

```json
{
  "test_cases": [
    {
      "category": "missing_diacritics",
      "input": "cong viec kinh doanh thi rat kho khan",
      "expected": "công việc kinh doanh thì rất khó khăn"
    },
    {
      "category": "typo",
      "input": "toi dang là sinh diên nam hai ở truong đạ hoc",
      "expected": "tôi đang là sinh viên năm hai ở trường đại học"
    },
    {
      "category": "sticky_words",
      "input": "Lần này anh Phươngqyết xếp hàng mua bằng được",
      "expected": "Lần này anh Phương quyết xếp hàng mua bằng được"
    },
    {
      "category": "mixed_case",
      "input": "một số chuyen gia tài chính ngâSn hànG của Việt Nam",
      "expected": "một số chuyên gia tài chính ngân hàng của Việt Nam"
    },
    {
      "category": "teencode",
      "note": "Chỉ test nếu dùng model yammdd",
      "input": "hum ni a bùn wá bé iu ưi",
      "expected": "hôm nay anh buồn quá bé yêu ơi"
    },
    {
      "category": "correct_text",
      "note": "Văn bản đúng - model không nên thay đổi",
      "input": "Việt Nam là một quốc gia nằm ở Đông Nam Á",
      "expected": "Việt Nam là một quốc gia nằm ở Đông Nam Á"
    },
    {
      "category": "long_text",
      "input": "Nefn kinh té thé giới đang đúng trươc nguyen co của mọt cuoc suy thoai kinh te nghiem trog va dai keo dài trong nhieu nam",
      "expected": "Nền kinh tế thế giới đang đứng trước nguyên cơ của một cuộc suy thoái kinh tế nghiêm trọng và dai kéo dài trong nhiều năm"
    },
    {
      "category": "special_chars",
      "input": "Giá dầu WTI giảm 2.5% xuống còn 75.3 USD/thùng",
      "expected": "Giá dầu WTI giảm 2.5% xuống còn 75.3 USD/thùng",
      "note": "Số, ký hiệu không nên bị sửa"
    }
  ]
}
```

### 10.2 Benchmark Performance

```python
# scripts/benchmark.py
"""
Benchmark inference speed trên CPU và GPU.

Test:
- 100 câu ngắn (< 30 từ): target < 500ms/câu (CPU)
- 50 câu trung bình (30-80 từ): target < 1500ms/câu (CPU)
- 10 câu dài (> 80 từ): target < 3000ms/câu (CPU)
- Batch processing: 1 trang A4 (~300 từ): target < 15 giây (CPU)
- Memory usage: peak < 2GB
- Model load time: < 10 giây (CPU)
"""
```

---

## 11. Roadmap

### Phase 1: MVP (4-6 tuần)

**Tuần 1-2: Core Engine**
- [ ] Setup project structure
- [ ] Download & convert model sang ONNX INT8
- [ ] Implement Preprocessor (tách câu)
- [ ] Implement Inference Engine (ONNX Runtime)
- [ ] Implement Postprocessor (diff)
- [ ] Unit tests cho engine

**Tuần 3-4: UI**
- [ ] Main window layout (split view)
- [ ] Text editor panel
- [ ] Diff viewer panel (highlighting)
- [ ] Accept/Reject workflow
- [ ] Settings dialog
- [ ] Light/Dark theme
- [ ] Keyboard shortcuts

**Tuần 5: Integration & Polish**
- [ ] Connect UI ↔ Engine qua QThread
- [ ] Progress bar & status updates
- [ ] File import (TXT, DOCX)
- [ ] Export (Copy, TXT, DOCX)
- [ ] Batch processing tab
- [ ] Error handling & logging

**Tuần 6: Packaging & Testing**
- [ ] PyInstaller build script
- [ ] Inno Setup installer
- [ ] Test trên Windows 10 & 11
- [ ] Test trên máy 4GB RAM / 8GB RAM
- [ ] Performance benchmark
- [ ] Fix bugs, polish UX

### Phase 2: Enhanced (4 tuần)

- [ ] Tích hợp Ollama cho LLM inference (GPU users)
- [ ] Model download manager (tải model bổ sung từ trong app)
- [ ] Auto-update mechanism
- [ ] Custom dictionary (thêm từ không sửa)
- [ ] History (lưu lại các lần sửa gần đây)

### Phase 3: Plugin (4 tuần)

- [ ] Word COM Add-in (pywin32)
- [ ] Excel COM Add-in
- [ ] System tray mode (sửa lỗi từ clipboard)
- [ ] Chrome Extension (optional, connect qua local server)

---

## 12. Dependencies (requirements.txt)

```
# Core
PyQt6>=6.5.0
onnxruntime>=1.16.0               # CPU inference
# onnxruntime-gpu>=1.16.0         # GPU inference (optional)

# Model & Tokenizer
transformers>=4.35.0
optimum[onnxruntime]>=1.14.0
sentencepiece>=0.1.99

# File handling
python-docx>=1.1.0                # Read/write DOCX

# Utilities
# (không cần thêm, dùng stdlib: difflib, re, json, logging, pathlib)

# Build & Packaging
# PyInstaller>=6.0 (dev only)
# onnx>=1.15.0 (dev only, for conversion)
```

---

## 13. Rủi ro & Giải pháp

| Rủi ro | Mức độ | Giải pháp |
|---|---|---|
| Model ONNX quá lớn (>1GB) | Trung bình | Quantize INT8, nén model, lazy loading |
| Inference chậm trên CPU yếu | Trung bình | Tăng num_beams=1 (greedy), giảm max_length, cache |
| Model sửa sai (over-correction) | Cao | Cho user review từng change, nút Reject, custom dict |
| Model không sửa được tên riêng | Thấp | Postprocessor: detect & skip proper nouns |
| PyInstaller build quá nặng | Trung bình | Exclude unnecessary packages, UPX compression |
| Antivirus block .exe | Trung bình | Code signing certificate, submit to Microsoft SmartScreen |
| Conflict ONNX Runtime + CUDA | Thấp | Fallback về CPU nếu GPU init fail |
| Tokenizer mismatch | Thấp | Ship tokenizer cùng model, pin version |

---

## 14. Metrics thành công

- **Accuracy:** ≥ 90% word accuracy trên bộ test (mục 10.1)
- **Speed:** ≤ 500ms/câu trên CPU i5 + 8GB RAM
- **Installer size:** ≤ 700MB
- **RAM usage:** ≤ 2GB khi processing
- **User satisfaction:** Ứng dụng chạy được từ lần đầu mở, không cần cấu hình phức tạp

---

## Phụ lục A: Lệnh nhanh để bắt đầu

```bash
# 1. Tạo environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Cài dependencies
pip install PyQt6 transformers optimum[onnxruntime] onnxruntime sentencepiece python-docx

# 3. Download & convert model
python scripts/download_model.py
python scripts/convert_to_onnx.py
python scripts/quantize_model.py

# 4. Test inference
python -c "
from src.engine.inference import CorrectionEngine
engine = CorrectionEngine('./models/bartpho-correction-v2-onnx-int8')
engine.load()
print(engine.correct('toi dang hoc AI o truong dai hoc'))
"

# 5. Chạy app
python src/main.py

# 6. Build exe
pyinstaller installer/build_exe.py
```

## Phụ lục B: Tham khảo

- Model chính: https://huggingface.co/bmd1905/vietnamese-correction-v2
- Model phụ: https://huggingface.co/yammdd/vietnamese-error-correction
- Base model: https://huggingface.co/vinai/bartpho-syllable
- ONNX Runtime: https://onnxruntime.ai/docs/
- Optimum ONNX export: https://huggingface.co/docs/optimum/onnxruntime/usage_guides/export
- PyQt6: https://doc.qt.io/qtforpython-6/
- PyInstaller: https://pyinstaller.org/en/stable/
- Inno Setup: https://jrsoftware.org/isinfo.php