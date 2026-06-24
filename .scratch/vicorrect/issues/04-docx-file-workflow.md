# Import và export DOCX

Status: ready-for-agent

## What to build

Cho phép người dùng đưa tài liệu DOCX qua cùng correction/review flow và xuất lại một DOCX giữ được cấu trúc cùng định dạng cơ bản. Nội dung không được hỗ trợ để sửa phải được bảo toàn thay vì bị loại khỏi tài liệu.

## Acceptance criteria

- [ ] Người dùng có thể mở hoặc kéo thả một file `.docx`, xem nội dung các paragraph theo đúng thứ tự và chạy correction flow hiện có.
- [ ] Import giữ ranh giới paragraph để kết quả review và export không gộp các đoạn ngoài ý muốn.
- [ ] Export giữ thứ tự paragraph, paragraph style và định dạng run cơ bản gồm bold, italic và underline ở phần nội dung không thay đổi.
- [ ] Text mới được model tạo ra kế thừa định dạng từ span gốc gần nhất theo một quy tắc nhất quán và có test.
- [ ] Bảng, hình ảnh, header/footer và các thành phần chưa được correction flow hỗ trợ vẫn được giữ nguyên trong file xuất.
- [ ] Save-as DOCX và **Replace original** có cùng bảo vệ xác nhận/ghi an toàn như workflow TXT.
- [ ] File hỏng, file có mật khẩu hoặc lỗi quyền truy cập được báo rõ mà không làm crash ứng dụng hay phá file nguồn.
- [ ] Test round-trip dùng fixture có nhiều paragraph, style, bold/italic/underline, bảng và hình để phát hiện mất nội dung hoặc định dạng ngoài phạm vi.

## Blocked by

- [03 — Import, kéo thả và export TXT](03-txt-file-workflow.md)

## Comments

