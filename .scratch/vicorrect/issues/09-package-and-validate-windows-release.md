# Đóng gói và kiểm chứng bản phát hành Windows

Status: ready-for-agent

## What to build

Tạo quy trình release có thể lặp lại để đóng gói ViCorrect cùng primary model thành ứng dụng Windows onedir và installer không cần quyền admin. Kiểm chứng bản cài đặt sạch đáp ứng các cam kết offline, tương thích, hiệu năng và tài nguyên của MVP, đồng thời cung cấp tài liệu cho người dùng và maintainer.

## Acceptance criteria

- [ ] Build PyInstaller onedir tạo ứng dụng GUI không mở console và bao gồm PyQt6 plugins, ONNX Runtime, tokenizer, resources cùng primary ONNX INT8 model cần thiết.
- [ ] Inno Setup tạo installer versioned, cài mặc định vào LocalAppData không cần admin, có Start Menu/Desktop shortcut tùy chọn và uninstaller hoạt động.
- [ ] Bản cài sạch chạy được trên Windows 10 và Windows 11 64-bit mà không cần Python hoặc kết nối internet.
- [ ] Sau khi ngắt mạng, smoke test xác nhận nhập văn bản, correction, review, TXT/DOCX round-trip, settings và batch vẫn hoạt động.
- [ ] Installer không vượt quá 700 MB và yêu cầu tối đa 1.5 GB disk trống; sai lệch phải được đo, giải thích và đưa về trong target trước khi hoàn thành issue.
- [ ] Trên máy CPU 8 GB đại diện, app khởi động dưới 5 giây, load model dưới 10 giây, câu ≤30 từ dưới 500 ms, trang khoảng 300 từ dưới 15 giây và processing RAM dưới 2 GB.
- [ ] Trên cấu hình 4 GB RAM đại diện, app hoàn thành correction cơ bản hoặc từ chối có kiểm soát với hướng dẫn rõ, không bị hệ điều hành kill do vượt bộ nhớ.
- [ ] Nếu có môi trường RTX 3060+ trong release matrix, benchmark ghi nhận startup/load/inference, VRAM và CPU fallback; thiếu môi trường GPU được ghi rõ trong release evidence thay vì giả lập kết quả đạt.
- [ ] Build tạo version metadata, log chẩn đoán không chứa toàn bộ văn bản người dùng theo mặc định và hướng dẫn vị trí log khi cần support.
- [ ] User guide bằng tiếng Việt mô tả cài đặt, correction/review, file workflow, batch, settings, privacy offline và lỗi thường gặp.
- [ ] Developer guide mô tả setup, model artifact pipeline, test, benchmark, build installer và cách tái tạo release từ source checkout sạch.
- [ ] Release checklist lưu bằng chứng test/benchmark, checksum artifact và mọi giới hạn đã biết; build thất bại nếu model/resources bắt buộc bị thiếu.

## Blocked by

- [02 — Review và tạo bản sửa cuối cùng](02-review-and-finalize-corrections.md)
- [03 — Import, kéo thả và export TXT](03-txt-file-workflow.md)
- [04 — Import và export DOCX](04-docx-file-workflow.md)
- [05 — Hủy tác vụ và phục hồi an toàn](05-cancel-and-recover.md)
- [06 — Cấu hình model, device và hiệu năng](06-runtime-and-model-settings.md)
- [07 — Giao diện cá nhân hóa và song ngữ](07-appearance-and-language.md)
- [08 — Batch correction TXT/DOCX](08-batch-correction.md)

## Comments

