from flask import Flask, render_template, request, jsonify, send_file
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import json
import hashlib
import re
import img2pdf
import tempfile

app = Flask(__name__)

# Configuration
DATA_FOLDER = 'Data'
UPLOAD_FOLDER = 'static/page_images'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cache for OCR results to avoid re-processing
ocr_cache = {}

# File mapping configuration
# Maps: Document Type -> Authority -> PDF File Path
FILE_MAPPING = {
    'الهيكل التنظيمي': {
        'هيئة البحرين للثقافة والاثار': 'Data/الهيكل التنظيمي/هيئة البحرين للثقافة والاثار.pdf',
        'وزارة الاشغال': 'Data/الهيكل التنظيمي/وزارة الاشغال.pdf'
    },
    'الوصف الوظيفي': {
        'هيئة البحرين للثقافة والاثار': 'Data/الوصف الوظيفي/هيئة البحرين للثقافة والاثار.pdf',
        # 'وزارة الاشغال': 'Data/الوصف الوظيفي/وزارة الاشغال.pdf'  # Add when available
    }
}

# Available authorities for each document type
AUTHORITIES = {
    'الهيكل التنظيمي': ['هيئة البحرين للثقافة والاثار', 'وزارة الاشغال'],
    'الوصف الوظيفي': ['هيئة البحرين للثقافة والاثار']
}


def sanitize_filename(filename):
    """Remove special characters from filename"""
    # Remove or replace special characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename


def get_cache_key(pdf_path, page_num=None):
    """Generate cache key for OCR results"""
    mtime = os.path.getmtime(pdf_path) if os.path.exists(pdf_path) else 0
    key = f"{pdf_path}_{page_num}_{mtime}"
    return hashlib.md5(key.encode()).hexdigest()


def extract_text_from_pdf(pdf_path, page_num=None):
    """
    Extract text from PDF using OCR with Arabic and English support.
    Returns a list of dictionaries with page number and extracted text.
    """
    try:
        # Check cache first
        cache_key = get_cache_key(pdf_path, page_num)
        if cache_key in ocr_cache:
            return ocr_cache[cache_key]
        
        # Convert PDF pages to images
        if page_num is not None:
            # Extract specific page (1-indexed in pdf2image, but we use 0-indexed internally)
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=300)
        else:
            images = convert_from_path(pdf_path, dpi=300)
        
        results = []
        for idx, image in enumerate(images):
            try:
                # Perform OCR with Arabic and English language support
                # Using 'ara+eng' for Arabic and English
                text = pytesseract.image_to_string(image, lang='ara+eng')
                actual_page = page_num if page_num is not None else idx
                results.append({
                    'page': actual_page,
                    'text': text,
                    'image': image
                })
            except Exception as e:
                print(f"Error in OCR for page {idx}: {str(e)}")
                # Try with English only if Arabic fails
                try:
                    text = pytesseract.image_to_string(image, lang='eng')
                    actual_page = page_num if page_num is not None else idx
                    results.append({
                        'page': actual_page,
                        'text': text,
                        'image': image
                    })
                except:
                    # If OCR completely fails, still include the page with empty text
                    actual_page = page_num if page_num is not None else idx
                    results.append({
                        'page': actual_page,
                        'text': '',
                        'image': image
                    })
        
        # Cache results
        ocr_cache[cache_key] = results
        return results
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return []


def search_in_pdf(pdf_path, search_term):
    """
    Search for a term in a PDF file.
    Returns a list of matches with page numbers and images.
    """
    matches = []
    
    # Extract text from all pages
    pages_data = extract_text_from_pdf(pdf_path)
    
    # Search for the term in each page
    for page_data in pages_data:
        page_text = page_data['text']
        page_num = page_data['page']
        page_image = page_data['image']
        
        # Case-insensitive search (handle both Arabic and English)
        search_lower = search_term.lower()
        text_lower = page_text.lower()
        
        # Also try direct match for Arabic text (case sensitivity matters less)
        if search_lower in text_lower or search_term in page_text:
            # Save page image with sanitized filename
            pdf_basename = sanitize_filename(os.path.basename(pdf_path))
            image_filename = f"page_{pdf_basename}_{page_num}.png"
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            page_image.save(image_path, 'PNG')
            
            matches.append({
                'page': page_num + 1,  # Convert to 1-indexed for display
                'image_path': f'/static/page_images/{image_filename}',
                'image_file': image_filename,  # Store filename for PDF generation
                'pdf_name': os.path.basename(pdf_path)
            })
    
    return matches


@app.route('/')
def index():
    """Main page with search interface"""
    return render_template('index.html')


@app.route('/api/authorities', methods=['POST'])
def get_authorities():
    """Get list of authorities for a given document type"""
    data = request.get_json()
    doc_type = data.get('document_type', '')
    
    authorities = AUTHORITIES.get(doc_type, [])
    return jsonify({'authorities': authorities})


@app.route('/api/search', methods=['POST'])
def search():
    """Perform search in PDF"""
    data = request.get_json()
    doc_type = data.get('document_type', '')
    authority = data.get('authority', '')
    search_term = data.get('search_term', '').strip()
    
    if not doc_type or not authority or not search_term:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get PDF path from mapping
    pdf_path = FILE_MAPPING.get(doc_type, {}).get(authority)
    
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404
    
    # Perform search
    matches = search_in_pdf(pdf_path, search_term)
    
    return jsonify({
        'matches': matches,
        'total_matches': len(matches),
        'pdf_name': os.path.basename(pdf_path)
    })


@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF from search result images"""
    data = request.get_json()
    image_files = data.get('image_files', [])
    pdf_name = data.get('pdf_name', 'search_results')
    search_term = data.get('search_term', '')
    
    if not image_files:
        return jsonify({'error': 'No images to convert'}), 400
    
    try:
        # Get full paths to image files
        image_paths = []
        for img_file in image_files:
            img_path = os.path.join(UPLOAD_FOLDER, img_file)
            if os.path.exists(img_path):
                image_paths.append(img_path)
        
        if not image_paths:
            return jsonify({'error': 'Image files not found'}), 404
        
        # Sort by page number (extract from filename)
        def get_page_num(path):
            try:
                # Extract page number from filename like "page_filename_0.png"
                basename = os.path.basename(path)
                parts = basename.split('_')
                if len(parts) >= 3:
                    return int(parts[-1].replace('.png', ''))
            except:
                return 0
            return 0
        
        image_paths.sort(key=get_page_num)
        
        # Create PDF from images
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdf_bytes = img2pdf.convert(image_paths)
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        
        # Create download filename
        safe_search_term = sanitize_filename(search_term)[:30]  # Limit length
        safe_pdf_name = sanitize_filename(pdf_name)[:30]
        download_filename = f"{safe_pdf_name}_{safe_search_term}_results.pdf"
        
        return send_file(
            tmp_pdf_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


def check_dependencies():
    """Check if required dependencies are installed"""
    errors = []
    
    # Check Tesseract
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        errors.append(f"Tesseract OCR not found: {str(e)}. Please install Tesseract OCR.")
    
    # Check if Arabic language pack is available
    try:
        available_langs = pytesseract.get_languages()
        if 'ara' not in available_langs:
            errors.append("Arabic language pack (ara) not found. OCR may not work correctly for Arabic text.")
    except:
        pass  # If we can't check, continue anyway
    
    if errors:
        print("WARNING: Dependency issues found:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease install missing dependencies before using the application.")
        print("See README.md for installation instructions.\n")
    
    return len(errors) == 0


if __name__ == '__main__':
    print("Starting PDF Search System...")
    check_dependencies()
    port = 5001
    print(f"Server starting on http://localhost:{port}")
    print(f"Open this URL in your browser: http://localhost:{port}")
    app.run(debug=True, port=port)

