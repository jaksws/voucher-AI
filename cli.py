import argparse
import os
import numpy as np
from PIL import Image
from core.extractor import VoucherExtractor
from core.pdf_processor import PDFProcessor
from core.voucher_detector import VoucherDetector

def process_pdf(file):
    pdf_processor = PDFProcessor()
    extractor = VoucherExtractor()
    images = pdf_processor.pdf_to_images(file)
    results = {}
    for img, meta in images:
        voucher_num = extractor.extract_voucher_number(img)
        results[f"Page_{meta['page']}"] = {
            'voucher_number': voucher_num,
            'metadata': meta
        }
    return results

def process_image(file):
    img = np.array(Image.open(file))
    detector = VoucherDetector()
    roi = detector.detect_roi(img)
    extractor = VoucherExtractor()
    voucher_num = extractor.extract_voucher_number(roi)
    return {'voucher_number': voucher_num}

def main():
    parser = argparse.ArgumentParser(description="Voucher AI CLI - استخراج رقم السند من PDF أو صورة")
    parser.add_argument('file', help='مسار ملف PDF أو صورة')
    args = parser.parse_args()
    file = args.file
    if file.lower().endswith('.pdf'):
        results = process_pdf(file)
    else:
        results = process_image(file)
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
