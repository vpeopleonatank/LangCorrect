# Import, kéo thả và export TXT

Status: ready-for-agent

## What to build

Mở rộng correction flow thành một workflow file TXT hoàn chỉnh: người dùng mở hoặc kéo thả file, sửa và review nội dung, sau đó lưu thành file mới hoặc thay thế file nguồn một cách an toàn.

## Acceptance criteria

- [ ] Người dùng có thể chọn file `.txt` từ file dialog hoặc kéo thả đúng một file hợp lệ vào cửa sổ.
- [ ] File TXT UTF-8, có hoặc không có BOM, được đọc đúng; xuống dòng được giữ trong editor.
- [ ] App ghi nhớ đường dẫn nguồn và thể hiện rõ văn bản hiện tại đến từ file nào.
- [ ] File không hỗ trợ, encoding không đọc được và lỗi quyền truy cập tạo thông báo rõ ràng mà không làm mất nội dung đang mở.
- [ ] Người dùng có thể lưu văn bản cuối cùng thành TXT UTF-8 qua file dialog.
- [ ] **Replace original** chỉ khả dụng khi phiên hiện tại được import từ file và luôn yêu cầu xác nhận trước khi ghi đè.
- [ ] Ghi đè dùng quy trình an toàn để lỗi giữa chừng không làm hỏng hoặc xóa file gốc.
- [ ] App cảnh báo trước khi mở file khác nếu editor có thay đổi chưa được lưu hoặc chưa hoàn tất review.
- [ ] Status bar báo chính xác file đã mở/lưu/thay thế.
- [ ] Test tự động bao phủ UTF-8/BOM, newline, drag-drop validation, save-as, overwrite confirmation và lỗi I/O.

## Blocked by

- [02 — Review và tạo bản sửa cuối cùng](02-review-and-finalize-corrections.md)

## Comments

