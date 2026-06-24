# Offline model artifacts

ViCorrect mặc định tìm model offline ở thư mục này.

Quy trình chuẩn bị:

1. `python scripts\download_model.py`
2. `python scripts\convert_to_onnx.py`
3. `python scripts\quantize_model.py`

Artifact cuối cùng nên nằm tại `models/bartpho-correction-v2-onnx-int8`.
