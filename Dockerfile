# صورة أساس محدثة وصغيرة
FROM python:3.11-slim

# تثبيت التبعيات النظامية مع التنظيف لتقليل الحجم
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ara \
    libgl1-mesa-glx \
    poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت الحزم باستخدام PyTorch source
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --find-links https://download.pytorch.org/whl/torch_stable.html -r requirements.txt

# نسخ الكود
COPY . .

# كشف المنفذ إذا كنت تستخدم FastAPI
EXPOSE 8000

# نقطة البداية للتطبيق (API)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
