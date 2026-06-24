# Cấu hình model, device và hiệu năng

Status: ready-for-agent

## What to build

Thêm settings cho model đã cài đặt, device, giới hạn token và batch size; tự nhận diện phần cứng rồi chọn cấu hình an toàn. Cấu hình phải được lưu qua các phiên và GPU lỗi phải fallback về CPU thay vì chặn người dùng.

## Acceptance criteria

- [ ] Settings hiển thị các model hợp lệ từ registry artifact đã cài đặt và chọn model chính làm mặc định.
- [ ] Model `yammdd/vietnamese-error-correction` chỉ xuất hiện nếu artifact tương thích đã có sẵn; issue này không tải model và không hiển thị lựa chọn không dùng được.
- [ ] Device có ba lựa chọn **Auto**, **CPU**, **GPU**, trong đó **Auto** là mặc định.
- [ ] Auto dùng GPU provider tương thích khi thực sự khả dụng, nếu không dùng CPU; không suy luận GPU chỉ từ tên phần cứng.
- [ ] Nếu GPU được yêu cầu nhưng khởi tạo thất bại, app fallback về CPU, tiếp tục hoạt động và thông báo lý do cho người dùng.
- [ ] Max tokens mặc định 256 và batch size mặc định 1; giá trị nhập được validate bằng giới hạn an toàn trước khi lưu.
- [ ] Hardware summary cho biết RAM, inference provider khả dụng và cấu hình được khuyến nghị mà không yêu cầu mạng.
- [ ] Thay đổi model/device được áp dụng cho job kế tiếp bằng lifecycle load/unload rõ ràng; không giữ đồng thời model cũ không cần thiết trong RAM.
- [ ] Settings được lưu và khôi phục qua lần khởi động tiếp theo; cấu hình hỏng hoặc model mất file tự quay về mặc định an toàn.
- [ ] Test tự động mô phỏng CPU-only, GPU khả dụng, GPU init failure, registry có/không có model phụ và persistence lỗi.

## Blocked by

- [01 — Sửa văn bản nhập trực tiếp bằng model offline](01-correct-entered-text-offline.md)

## Comments

