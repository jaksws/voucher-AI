from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QWidget, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import json
import numpy as np
from PIL import Image
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.extractor import VoucherExtractor
from core.pdf_processor import PDFProcessor
from core.voucher_detector import VoucherDetector

class AIWorker(QThread):
    finished = pyqtSignal(object)
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
    def run(self):
        result = self.func(*self.args)
        self.finished.emit(result)

class VoucherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.extractor = VoucherExtractor()
        self.detector = VoucherDetector()
        self.pdf_processor = PDFProcessor()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("منصة معالجة السندات الذكية")
        self.setGeometry(100, 100, 800, 600)
        self.btn_pdf = QPushButton("معالجة PDF", self)
        self.btn_image = QPushButton("معالجة صورة", self)
        self.progress = QProgressBar(self)
        self.result_area = QTextEdit(self)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("اختر ملف السندات:"))
        layout.addWidget(self.btn_pdf)
        layout.addWidget(self.btn_image)
        layout.addWidget(self.progress)
        layout.addWidget(self.result_area)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.btn_pdf.clicked.connect(self.process_pdf)
        self.btn_image.clicked.connect(self.process_image)
    def process_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "اختر ملف PDF", "", "PDF Files (*.pdf)")
        if file:
            self.progress.setValue(10)
            self.worker = AIWorker(self._process_pdf, file)
            self.worker.finished.connect(self.show_result)
            self.worker.start()
    def process_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Image Files (*.png *.jpg *.jpeg)")
        if file:
            self.progress.setValue(10)
            self.worker = AIWorker(self._process_image, file)
            self.worker.finished.connect(self.show_result)
            self.worker.start()
    def _process_pdf(self, file):
        images = self.pdf_processor.pdf_to_images(file)
        results = {}
        for img, meta in images:
            voucher_num = self.extractor.extract_voucher_number(img)
            results[f"Page_{meta['page']}"] = {
                'voucher_number': voucher_num,
                'metadata': meta
            }
        return results
    def _process_image(self, file):
        img = np.array(Image.open(file))
        roi = self.detector.detect_roi(img)
        voucher_num = self.extractor.extract_voucher_number(roi)
        return {'voucher_number': voucher_num}
    def show_result(self, result):
        self.progress.setValue(100)
        self.result_area.setText(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoucherApp()
    window.show()
    sys.exit(app.exec_())
