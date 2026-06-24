# Offline model artifacts

ViCorrect mặc định tìm model offline ở thư mục này.

Quy trình chuẩn bị:

1. `python scripts\download_model.py`
2. `python scripts\convert_to_onnx.py`
3. `python scripts\quantize_model.py`

App sẽ ưu tiên `models/bartpho-correction-v2-onnx` để có chất lượng tốt hơn, và dùng `models/bartpho-correction-v2-onnx-int8` làm phương án fallback khi cần artifact nhỏ hơn.
