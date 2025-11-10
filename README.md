# نظام البحث الذكي في ملفات PDF
## Intelligent PDF Search System

نظام بحث ذكي يسمح بالبحث في ملفات PDF التي تحتوي على صور (غير قابلة للبحث مباشرة) باستخدام تقنية OCR مع دعم اللغة العربية والإنجليزية.

An intelligent search system that allows searching within image-based PDF files using OCR technology with support for both Arabic and English languages.

## المتطلبات / Requirements

### Python Packages
```bash
pip install -r requirements.txt
```

### System Dependencies

#### macOS
```bash
brew install poppler tesseract tesseract-lang
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng
```

#### Windows
1. Download and install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
3. Add both to your system PATH

## الإعداد / Setup

1. **تأكد من تثبيت جميع المتطلبات** / Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **تحقق من الإعداد** / Verify setup:
   ```bash
   python check_setup.py
   ```
   This script will check if all dependencies are correctly installed.

3. **تأكد من وجود ملفات PDF في مجلد Data** / Ensure PDF files are in the Data folder

4. **قم بتحديث ملف app.py** / Update app.py:
   - تأكد من أن مسارات الملفات في `FILE_MAPPING` صحيحة
   - Ensure file paths in `FILE_MAPPING` are correct

## التشغيل / Running

```bash
python app.py
```

ثم افتح المتصفح على: `http://localhost:5000`

Then open your browser at: `http://localhost:5000`

## الاستخدام / Usage

1. **اختر نوع المستند** / Select Document Type:
   - الهيكل التنظيمي (Organizational Structure)
   - الوصف الوظيفي (Job Description)

2. **اختر الجهة** / Select Authority:
   - القائمة تتحدث تلقائياً بناءً على نوع المستند المختار
   - The list updates automatically based on the selected document type

3. **أدخل كلمة البحث** / Enter Search Term:
   - يمكن البحث بالعربية أو الإنجليزية
   - You can search in Arabic or English

4. **انقر على زر البحث** / Click Search Button

5. **عرض النتائج** / View Results:
   - اسم الملف / File name
   - رقم الصفحة / Page number
   - صورة الصفحة / Page image

## هيكل المشروع / Project Structure

```
Ptoject/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── page_images/      # Generated page images (auto-created)
└── Data/                 # PDF files folder
    ├── الهيكل التنظيمي/
    └── الوصف الوظيفي/
```

## ملاحظات / Notes

- المرة الأولى للبحث في ملف PDF قد تستغرق وقتاً أطول لأن النظام يقوم بتحويل جميع الصفحات
- First search in a PDF file may take longer as the system converts all pages

- الصور المحفوظة في `static/page_images/` يتم إنشاؤها تلقائياً عند البحث
- Images saved in `static/page_images/` are automatically created during search

- يمكنك إضافة ملفات PDF جديدة عن طريق تحديث `FILE_MAPPING` في `app.py`
- You can add new PDF files by updating `FILE_MAPPING` in `app.py`

## الدعم / Support

لأي مشاكل أو استفسارات، يرجى التحقق من:
- تثبيت Tesseract OCR بشكل صحيح
- تثبيت Poppler بشكل صحيح
- صحة مسارات الملفات في `FILE_MAPPING`

For any issues or questions, please check:
- Tesseract OCR is installed correctly
- Poppler is installed correctly
- File paths in `FILE_MAPPING` are correct

