from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os
import numpy as np
from core.pdf_processor import PDFProcessor
from core.extractor import VoucherExtractor
from core.voucher_detector import VoucherDetector
from PIL import Image

app = FastAPI(title="Voucher AI API")

@app.post("/extract")
async def extract_voucher(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        if file.filename.lower().endswith('.pdf'):
            pdf_processor = PDFProcessor()
            extractor = VoucherExtractor()
            images = pdf_processor.pdf_to_images(tmp_path)
            results = {}
            for img, meta in images:
                voucher_num = extractor.extract_voucher_number(img)
                results[f"Page_{meta['page']}"] = {
                    'voucher_number': voucher_num,
                    'metadata': meta
                }
        else:
            img = np.array(Image.open(tmp_path))
            detector = VoucherDetector()
            roi = detector.detect_roi(img)
            extractor = VoucherExtractor()
            voucher_num = extractor.extract_voucher_number(roi)
            results = {'voucher_number': voucher_num}
        os.unlink(tmp_path)
        return JSONResponse({
            "success": True,
            "result": results,
            "filename": file.filename
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
