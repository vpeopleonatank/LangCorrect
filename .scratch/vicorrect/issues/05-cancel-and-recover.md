# Hủy tác vụ và phục hồi an toàn

Status: ready-for-agent

## What to build

Thêm khả năng hủy correction đang chạy mà không làm treo UI, rò worker hoặc hiển thị kết quả dở dang. Sau khi hủy, người dùng phải có thể chỉnh input và chạy lại ngay trong cùng phiên.

## Acceptance criteria

- [ ] Nút **Cancel** chỉ xuất hiện hoặc được bật khi correction đang chạy và phản hồi ngay khi người dùng kích hoạt.
- [ ] Việc hủy được kiểm tra giữa các câu/batch; inference call đang thực thi được kết thúc an toàn trước khi worker dừng nếu runtime không hỗ trợ ngắt cứng.
- [ ] Kết quả một job đã bị hủy không bao giờ ghi đè kết quả hợp lệ trước đó hoặc xuất hiện muộn trong UI.
- [ ] Progress và status chuyển sang trạng thái đã hủy rõ ràng; các control trở về trạng thái có thể sử dụng.
- [ ] Không tạo văn bản cuối cùng từ kết quả một phần và không tự động lưu bất kỳ file nào.
- [ ] Người dùng có thể chạy correction mới ngay sau khi hủy mà không cần khởi động lại app hoặc load trùng model.
- [ ] Đóng cửa sổ trong lúc chạy thực hiện shutdown worker có giới hạn thời gian và không để process nền treo.
- [ ] Test tự động bao phủ hủy trước câu đầu, giữa nhiều câu, race giữa cancel/completion và chạy lại sau cancel.

## Blocked by

- [01 — Sửa văn bản nhập trực tiếp bằng model offline](01-correct-entered-text-offline.md)

## Comments

