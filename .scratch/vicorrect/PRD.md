# ViCorrect — Ứng dụng sửa lỗi chính tả tiếng Việt cho Windows

Status: Ready for implementation

Tài liệu nguồn: [docs/PRD.md](../../docs/PRD.md)

## Phạm vi issue set

Issue set này triển khai Phase 1 (MVP) của PRD: ứng dụng Windows độc lập, hoạt động offline, cho phép sửa, review và xuất văn bản tiếng Việt.

## Quyết định khi phân rã

- MVP đóng gói và sử dụng `bmd1905/vietnamese-correction-v2` làm model mặc định.
- Cấu hình model dựa trên registry các model đã được cài đặt.
- `yammdd/vietnamese-error-correction` chỉ xuất hiện khi artifact tương thích đã có sẵn; MVP không triển khai download manager hoặc hiển thị lựa chọn không sử dụng được.
- Download manager và trải nghiệm cài thêm model thuộc Phase 2.

## Issues

1. [Sửa văn bản nhập trực tiếp bằng model offline](issues/01-correct-entered-text-offline.md)
2. [Review và tạo bản sửa cuối cùng](issues/02-review-and-finalize-corrections.md)
3. [Import, kéo thả và export TXT](issues/03-txt-file-workflow.md)
4. [Import và export DOCX](issues/04-docx-file-workflow.md)
5. [Hủy tác vụ và phục hồi an toàn](issues/05-cancel-and-recover.md)
6. [Cấu hình model, device và hiệu năng](issues/06-runtime-and-model-settings.md)
7. [Giao diện cá nhân hóa và song ngữ](issues/07-appearance-and-language.md)
8. [Batch correction TXT/DOCX](issues/08-batch-correction.md)
9. [Đóng gói và kiểm chứng bản phát hành Windows](issues/09-package-and-validate-windows-release.md)

