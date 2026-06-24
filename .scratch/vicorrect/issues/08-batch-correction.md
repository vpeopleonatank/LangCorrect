# Batch correction TXT/DOCX

Status: ready-for-agent

## What to build

Thêm tab Batch để chọn nhiều file TXT/DOCX, sửa tuần tự bằng correction pipeline hiện có và tạo bản `_corrected` cạnh file nguồn. Vì batch không có review từng thay đổi, mọi đề xuất được tự động chấp nhận và report phải nói rõ số thay đổi đã tự động áp dụng.

## Acceptance criteria

- [ ] Người dùng có thể chọn hoặc kéo thả nhiều file TXT/DOCX và thấy một dòng duy nhất cho mỗi file hợp lệ.
- [ ] Mỗi file hiển thị trạng thái **Pending**, **Processing**, **Done**, **Error** hoặc **Cancelled**, cùng thông tin lỗi có thể hiểu được khi cần.
- [ ] File được xử lý tuần tự bằng cùng preprocessor, model settings và file round-trip behavior của workflow đơn file.
- [ ] Mọi thay đổi do model đề xuất trong batch được tự động accept; UI cảnh báo rõ điều này trước khi bắt đầu.
- [ ] Kết quả được lưu cùng thư mục với suffix `_corrected`, giữ đúng extension và không âm thầm ghi đè file đã tồn tại.
- [ ] Tên output trùng được giải quyết bằng quy tắc xác định, không làm mất file cũ.
- [ ] Lỗi ở một file không dừng các file còn lại; report giữ nguyên chi tiết lỗi theo file.
- [ ] Cancel dừng queue an toàn sau đơn vị công việc hiện tại, đánh dấu đúng các file chưa xử lý và không để output dở dang.
- [ ] Report cuối cùng gồm tổng số file, số Done/Error/Cancelled và tổng số thay đổi đã tự động áp dụng; người dùng có thể lưu report.
- [ ] Test tự động bao phủ queue hỗn hợp TXT/DOCX, file lỗi, tên output trùng, cancel giữa queue và thống kê report.

## Blocked by

- [04 — Import và export DOCX](04-docx-file-workflow.md)
- [05 — Hủy tác vụ và phục hồi an toàn](05-cancel-and-recover.md)
- [06 — Cấu hình model, device và hiệu năng](06-runtime-and-model-settings.md)

## Comments

