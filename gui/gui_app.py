from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QWidget, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import json
import numpy as np
from PIL import Image
import os
import requests
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
            self._process_file(file, is_pdf=True)

    def process_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Image Files (*.png *.jpg *.jpeg)")
        if file:
            self._process_file(file, is_pdf=False)

    def _process_file(self, file, is_pdf):
        self.progress.setValue(0)
        try:
            url = "http://localhost:8000/extract"
            with open(file, 'rb') as f:
                files = {'file': (file, f)}
                response = requests.post(url, files=files)
            if response.status_code == 200:
                result = response.json()
                self.show_result(result)
            else:
                self.result_area.setText(f"خطأ: {response.text}")
        except Exception as e:
            self.result_area.setText(f"حدث خطأ أثناء المعالجة: {str(e)}")
        finally:
            self.progress.setValue(100)

    def show_result(self, result):
        self.result_area.clear()
        if result.get("success"):
            self.result_area.setText(f"نتائج المعالجة:\n{result['result']}")
        else:
            self.result_area.setText(f"خطأ: {result.get('error', 'غير معروف')}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoucherApp()
    window.show()
    sys.exit(app.exec_())
