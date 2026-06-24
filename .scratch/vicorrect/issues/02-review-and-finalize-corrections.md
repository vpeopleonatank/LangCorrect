# Review và tạo bản sửa cuối cùng

Status: ready-for-agent

## What to build

Cho phép người dùng kiểm tra từng đề xuất của model trước khi dùng kết quả. Mỗi thay đổi có trạng thái độc lập, có thể Accept hoặc Reject bằng chuột hay bàn phím; ViCorrect tạo chính xác văn bản cuối cùng từ các lựa chọn hỗn hợp và cho phép copy vào clipboard.

## Acceptance criteria

- [ ] Mỗi thay đổi thêm, xóa hoặc thay thế được biểu diễn bằng một mục ổn định gắn với đúng vị trí trong văn bản gốc và bản sửa.
- [ ] Bản gốc và bản sửa highlight tương ứng: phần bị xóa/thay thế màu đỏ nhạt, phần thêm/thay thế mới màu xanh nhạt và trạng thái pending dễ nhận biết.
- [ ] Người dùng có thể chọn một thay đổi rồi Accept hoặc Reject mà không ảnh hưởng đến các thay đổi khác.
- [ ] **Accept All** và **Reject All** cập nhật toàn bộ thay đổi theo đúng ý nghĩa của nút.
- [ ] Counter luôn hiển thị đúng `X/Y thay đổi đã review`, kể cả khi không có thay đổi.
- [ ] `Tab` chuyển đến thay đổi pending tiếp theo, `Enter` Accept và `Delete` Reject; focus hiện tại luôn nhìn thấy được.
- [ ] Văn bản cuối cùng phản ánh đúng mọi tổ hợp Accept/Reject và giữ nguyên nội dung không liên quan, dấu câu cùng xuống dòng.
- [ ] Nút **Copy** sao chép văn bản cuối cùng vào clipboard và báo thành công trong status bar.
- [ ] Các hành động xuất kết quả chỉ được bật khi mọi thay đổi đã được review; trường hợp không có thay đổi được xem là đã hoàn tất review.
- [ ] Test tự động bao phủ diff có insert/delete/replace, thay đổi liền kề, Unicode tiếng Việt, Accept/Reject hỗn hợp và keyboard navigation.

## Blocked by

- [01 — Sửa văn bản nhập trực tiếp bằng model offline](01-correct-entered-text-offline.md)

## Comments

