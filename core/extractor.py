import easyocr
import pytesseract
import numpy as np
import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

def arabic_text_correction(text):
    # يمكن إضافة خوارزميات تصحيح متقدمة لاحقًا
    return text

class VoucherExtractor:
    def __init__(self):
        self.ocr_engine = config['ocr']['preferred_engine']
        self.tesseract_path = config['ocr']['tesseract_path']
        self.languages = config['ocr']['languages']
        if self.ocr_engine in ['hybrid', 'easyocr']:
            self.reader = easyocr.Reader(self.languages)
        if self.ocr_engine in ['hybrid', 'tesseract']:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

    def hybrid_ocr(self, img):
        text = ''
        if self.ocr_engine == 'hybrid':
            # دمج نتائج EasyOCR وTesseract
            result_easy = self.reader.readtext(img, detail=0, paragraph=True)
            result_tess = pytesseract.image_to_string(img, lang='+'.join(self.languages))
            text = '\n'.join(result_easy) + '\n' + result_tess
        elif self.ocr_engine == 'easyocr':
            result_easy = self.reader.readtext(img, detail=0, paragraph=True)
            text = '\n'.join(result_easy)
        else:
            text = pytesseract.image_to_string(img, lang='+'.join(self.languages))
        if config['processing']['arabic_text_correction']:
            text = arabic_text_correction(text)
        return text

    def smart_number_extraction(self, text):
        # استخراج رقم السند من النص (يمكن تحسينه لاحقًا)
        import re
        match = re.search(r'\b[0-9]{5,}\b', text)
        return match.group(0) if match else ''

    def extract_voucher_number(self, img):
        text = self.hybrid_ocr(img)
        return self.smart_number_extraction(text)
