from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ..diffing import ChangeType
from ..preprocessing import TextPreprocessor
from ..runtime import ModelRuntimeError, ModelSetupError, build_default_adapter
from ..workflow import CorrectionResult, CorrectionWorkflow


def _build_stylesheet() -> str:
    return """
    QMainWindow {
        background: #f8fafc;
    }
    QLabel#panelTitle {
        font-size: 15px;
        font-weight: 600;
        color: #0f172a;
    }
    QPlainTextEdit, QTextBrowser {
        background: white;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px;
        selection-background-color: #bfdbfe;
    }
    QPushButton {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: 600;
    }
    QPushButton:disabled {
        background: #94a3b8;
        color: #e2e8f0;
    }
    QStatusBar {
        background: #e2e8f0;
        color: #0f172a;
    }
    """


class CorrectionWorker(QObject):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, workflow: CorrectionWorkflow, text: str) -> None:
        super().__init__()
        self.workflow = workflow
        self.text = text
        self.logger = logging.getLogger(__name__)

    @pyqtSlot()
    def run(self) -> None:
        try:
            result = self.workflow.run(self.text, self.progress.emit)
        except (ModelSetupError, ModelRuntimeError) as exc:
            self.logger.exception("Correction workflow failed")
            self.failed.emit(str(exc))
        except Exception as exc:  # pragma: no cover - GUI only
            self.logger.exception("Unexpected correction failure")
            self.failed.emit(
                "Có lỗi không mong muốn khi sửa văn bản. Xem log tại logs/vicorrect.log rồi thử lại."
            )
        else:
            self.finished.emit(result)


@dataclass(frozen=True)
class TextStats:
    word_count: int
    character_count: int


class MainWindow(QMainWindow):
    def __init__(self, log_file: Path) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        self._thread: QThread | None = None
        self._worker: CorrectionWorker | None = None
        self._busy = False

        self.setWindowTitle("ViCorrect")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(_build_stylesheet())

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Nhập hoặc dán văn bản tiếng Việt tại đây...")
        self.editor.textChanged.connect(self._on_text_changed)

        self.corrected_view = QPlainTextEdit()
        self.corrected_view.setReadOnly(True)
        self.corrected_view.setPlaceholderText("Kết quả đã sửa sẽ xuất hiện ở đây.")

        self.diff_view = QTextBrowser()
        self.diff_view.setOpenExternalLinks(False)

        self.correct_button = QPushButton("Sửa lỗi")
        self.correct_button.clicked.connect(self._start_correction)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)

        self.progress_label = QLabel("Sẵn sàng")
        self.word_count_label = QLabel("0 từ")
        self.char_count_label = QLabel("0 ký tự")

        self.shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut.activated.connect(self._start_correction)
        self.numpad_shortcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
        self.numpad_shortcut.activated.connect(self._start_correction)

        self._build_layout()
        self._build_status_bar()
        self._refresh_actions()

    def _build_layout(self) -> None:
        left_layout = QVBoxLayout()
        left_title = QLabel("Văn bản gốc")
        left_title.setObjectName("panelTitle")
        left_layout.addWidget(left_title)
        left_layout.addWidget(self.editor)

        left_container = QWidget()
        left_container.setLayout(left_layout)

        right_layout = QVBoxLayout()
        corrected_title = QLabel("Kết quả đã sửa")
        corrected_title.setObjectName("panelTitle")
        diff_title = QLabel("Diff ban đầu")
        diff_title.setObjectName("panelTitle")
        right_layout.addWidget(corrected_title)
        right_layout.addWidget(self.corrected_view, stretch=3)
        right_layout.addWidget(diff_title)
        right_layout.addWidget(self.diff_view, stretch=2)

        right_container = QWidget()
        right_container.setLayout(right_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setSizes([430, 430])

        controls = QHBoxLayout()
        controls.addWidget(self.correct_button)
        controls.addWidget(self.progress_bar, stretch=1)
        controls.addWidget(self.progress_label)

        central_layout = QVBoxLayout()
        central_layout.addWidget(splitter, stretch=1)
        central_layout.addLayout(controls)

        central = QWidget()
        central.setLayout(central_layout)
        self.setCentralWidget(central)

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(self.word_count_label)
        status_bar.addPermanentWidget(self.char_count_label)
        self.setStatusBar(status_bar)
        self.statusBar().showMessage("Sẵn sàng")

    def _collect_stats(self) -> TextStats:
        text = self.editor.toPlainText()
        words = len([word for word in text.split() if word])
        return TextStats(word_count=words, character_count=len(text))

    def _on_text_changed(self) -> None:
        stats = self._collect_stats()
        self.word_count_label.setText(f"{stats.word_count} từ")
        self.char_count_label.setText(f"{stats.character_count} ký tự")
        self._refresh_actions()

    def _refresh_actions(self) -> None:
        has_text = bool(self.editor.toPlainText().strip())
        self.correct_button.setEnabled(has_text and not self._busy)

    def _build_workflow(self) -> CorrectionWorkflow:
        adapter = build_default_adapter(device="cpu")
        preprocessor = TextPreprocessor(max_tokens=16, token_counter=adapter)
        return CorrectionWorkflow(adapter=adapter, preprocessor=preprocessor)

    def _start_correction(self) -> None:
        text = self.editor.toPlainText()
        if self._busy or not text.strip():
            return

        self._busy = True
        self._refresh_actions()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_label.setText("Đang chuẩn bị model...")
        self.statusBar().showMessage("Đang sửa văn bản...")

        self._thread = QThread(self)
        self._worker = CorrectionWorker(self._build_workflow(), text)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_worker)
        self._thread.start()

    @pyqtSlot(int, int)
    def _on_progress(self, completed: int, total: int) -> None:
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(completed)
        self.progress_label.setText(f"{completed}/{total} câu")

    @pyqtSlot(object)
    def _on_finished(self, result: CorrectionResult) -> None:
        self.corrected_view.setPlainText(result.corrected_text)
        self.diff_view.setHtml(result.diff_html)
        change_count = len(
            [change for change in result.changes if change.change_type != ChangeType.EQUAL]
        )
        self.statusBar().showMessage(f"Đã sửa xong. Tìm thấy {change_count} thay đổi.")
        self.progress_label.setText("Hoàn tất")
        self.progress_bar.setVisible(False)
        self._busy = False
        self._refresh_actions()

    @pyqtSlot(str)
    def _on_failed(self, message: str) -> None:
        self.statusBar().showMessage("Không thể sửa văn bản.")
        self.progress_label.setText("Lỗi")
        self.progress_bar.setVisible(False)
        self._busy = False
        self._refresh_actions()
        QMessageBox.critical(
            self,
            "Không thể sửa văn bản",
            f"{message}\n\nLog: {self.log_file}",
        )

    @pyqtSlot()
    def _cleanup_worker(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None
