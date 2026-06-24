# Sửa văn bản nhập trực tiếp bằng model offline

Status: ready-for-agent

## What to build

Tạo tracer bullet đầu tiên của ViCorrect: người dùng mở ứng dụng Windows, gõ hoặc dán văn bản tiếng Việt, nhấn **Sửa lỗi** hoặc `Ctrl+Enter`, rồi nhận kết quả từ model BARTpho chạy hoàn toàn offline trong panel bên cạnh. Luồng phải bao gồm artifact ONNX INT8 có thể tái tạo, tokenizer tương ứng, tách câu an toàn, inference nền và diff trực quan ban đầu.

## Acceptance criteria

- [ ] Ứng dụng PyQt6 khởi chạy được với cửa sổ tối thiểu 800×500, hai panel có thể thay đổi kích thước và giao diện tiếng Việt mặc định.
- [ ] Người dùng có thể gõ hoặc dán văn bản; status bar cập nhật đúng số từ và số ký tự.
- [ ] Nút **Sửa lỗi** và `Ctrl+Enter` chạy cùng một correction flow và bị vô hiệu hóa hợp lý khi input rỗng hoặc tác vụ đang chạy.
- [ ] Có quy trình tái tạo được để lấy model chính, export sang ONNX, quantize INT8 và ghép đúng tokenizer; artifact lớn không bắt buộc commit vào Git.
- [ ] Runtime tải model chính và sửa văn bản mà không truy cập mạng sau khi model/tokenizer đã được cài đặt.
- [ ] Văn bản được tách theo ranh giới câu và tiếp tục chia các câu vượt quá 256 tokens mà không làm mất hoặc đảo thứ tự nội dung.
- [ ] Inference chạy ngoài UI thread; cửa sổ vẫn phản hồi và progress hiển thị `X/Y` câu đã hoàn thành.
- [ ] Panel kết quả hiển thị bản đã sửa và highlight các đoạn thêm, xóa hoặc thay thế bằng màu sắc phân biệt được.
- [ ] Thứ tự đoạn/câu và các xuống dòng có ý nghĩa được giữ khi ghép kết quả.
- [ ] Lỗi load model hoặc inference được log và hiển thị bằng thông báo có thể hành động, không làm ứng dụng crash.
- [ ] Test tự động bao phủ tách/ghép câu, giới hạn token, mapping progress, diff cơ bản và correction flow qua một inference adapter có thể thay thế trong test.

## Blocked by

None - can start immediately.

## Comments

