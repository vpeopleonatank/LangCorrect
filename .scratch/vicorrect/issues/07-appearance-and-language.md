# Giao diện cá nhân hóa và song ngữ

Status: ready-for-agent

## What to build

Cho phép người dùng thay đổi theme, ngôn ngữ giao diện và cỡ chữ editor mà không làm gián đoạn nội dung đang sửa. Các lựa chọn được áp dụng nhất quán trên toàn ứng dụng và được ghi nhớ.

## Acceptance criteria

- [ ] Theme có các lựa chọn **Light**, **Dark** và **System**; mặc định **System** phản ánh theme Windows hiện tại.
- [ ] Mọi control, dialog, trạng thái disabled/focus và diff highlight vẫn đọc rõ ở cả light và dark theme.
- [ ] UI có đầy đủ bản dịch tiếng Việt và English cho menu, nút, dialog, status, validation và error message do ứng dụng kiểm soát.
- [ ] Đổi ngôn ngữ cập nhật các thành phần UI đang mở mà không làm mất input, kết quả hoặc trạng thái review.
- [ ] Cỡ chữ editor có phạm vi an toàn, áp dụng đồng thời cho bản gốc và bản sửa nhưng không làm thay đổi cỡ chữ UI chung.
- [ ] Theme, ngôn ngữ và cỡ chữ được lưu, khôi phục ở lần chạy sau và quay về mặc định nếu cấu hình không hợp lệ.
- [ ] Layout vẫn sử dụng được ở minimum window size với cả hai ngôn ngữ và cỡ chữ lớn nhất được hỗ trợ.
- [ ] Test tự động xác minh translation coverage, persistence và mapping theme; có checklist visual smoke test cho các tổ hợp chính.

## Blocked by

- [01 — Sửa văn bản nhập trực tiếp bằng model offline](01-correct-entered-text-offline.md)

## Comments

