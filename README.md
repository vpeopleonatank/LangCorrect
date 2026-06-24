# ViCorrect

Tracer bullet đầu tiên cho ứng dụng sửa lỗi chính tả tiếng Việt chạy offline trên Windows.

## Tính năng của issue 01

- Giao diện PyQt6 hai panel với tiếng Việt mặc định.
- Sửa văn bản bằng model ONNX offline qua nút **Sửa lỗi** hoặc `Ctrl+Enter`.
- Tách câu an toàn, tiếp tục chia câu dài vượt giới hạn token mà vẫn giữ nguyên thứ tự và xuống dòng.
- Chạy inference ở background thread và hiển thị tiến trình `X/Y`.
- Hiển thị kết quả đã sửa cùng diff trực quan ban đầu.
- Cung cấp script tái tạo artifact model/tokenizer để cài offline.

## Cài đặt

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Chuẩn bị model offline

```powershell
python scripts\download_model.py --output-dir models\bartpho-correction-v2
python scripts\convert_to_onnx.py --model-dir models\bartpho-correction-v2 --output-dir models\bartpho-correction-v2-onnx
python scripts\quantize_model.py --model-dir models\bartpho-correction-v2-onnx --output-dir models\bartpho-correction-v2-onnx-int8
```

Có thể đặt biến môi trường `VICORRECT_MODEL_DIR` để app dùng artifact ở vị trí khác.
Mặc định app sẽ ưu tiên `models/bartpho-correction-v2-onnx` để giữ chất lượng gần với model gốc hơn, và chỉ rơi về `models/bartpho-correction-v2-onnx-int8` nếu không có bản ONNX thường.

## Chạy ứng dụng

```powershell
python src\main.py
```

## Test model Hugging Face thủ công

```powershell
python scripts\manual_test_hf_model.py
```

Có thể test nhanh nhiều câu:

```powershell
python scripts\manual_test_hf_model.py --text "toi dang hoc AI o truong dai hoc" --text "cam on ban rat nhieu"
```

Hoặc đọc input từ file UTF-8, mỗi dòng một câu:

```powershell
python scripts\manual_test_hf_model.py --file .scratch\manual-input.txt
```

## Chạy test

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```
