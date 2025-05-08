import numpy as np
from pdf2image import convert_from_path

class PDFProcessor:
    def __init__(self, dpi=300, poppler_path=r'C:/Program Files/poppler-23.11.0/Library/bin'):
        self.dpi = dpi
        self.poppler_path = poppler_path

    def pdf_to_images(self, pdf_path):
        """تحويل PDF إلى سلسلة صور مع الاحتفاظ ببيانات التعريف"""
        images = convert_from_path(
            pdf_path,
            dpi=self.dpi,
            thread_count=4,
            poppler_path=self.poppler_path
        )
        meta_images = []
        for i, img in enumerate(images):
            meta = {
                'page': i+1,
                'resolution': f"{img.size[0]}x{img.size[1]}",
                'format': img.mode
            }
            meta_images.append((np.array(img), meta))
        return meta_images
