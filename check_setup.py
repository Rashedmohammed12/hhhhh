#!/usr/bin/env python3
"""
Quick setup verification script
Checks if all dependencies are installed correctly
"""

import sys

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_packages():
    """Check if required Python packages are installed"""
    packages = {
        'flask': 'Flask',
        'pdf2image': 'pdf2image',
        'pytesseract': 'pytesseract',
        'PIL': 'Pillow'
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is NOT installed. Run: pip install {name}")
            all_ok = False
    
    return all_ok

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is installed (version: {version})")
        
        # Check for Arabic language pack
        try:
            langs = pytesseract.get_languages()
            if 'ara' in langs:
                print("✅ Arabic language pack (ara) is available")
            else:
                print("⚠️  Arabic language pack (ara) is NOT available")
                print("   Install it with: brew install tesseract-lang (macOS)")
                print("   or: sudo apt-get install tesseract-ocr-ara (Linux)")
        except:
            print("⚠️  Could not check for language packs")
        
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR is NOT installed or not found: {e}")
        print("   Install it with: brew install tesseract (macOS)")
        print("   or: sudo apt-get install tesseract-ocr (Linux)")
        return False

def check_poppler():
    """Check if Poppler is installed"""
    try:
        from pdf2image import convert_from_path
        # Try to import poppler (indirect check)
        import subprocess
        result = subprocess.run(['pdftoppm', '-v'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0 or 'pdftoppm' in result.stderr:
            print("✅ Poppler is installed")
            return True
    except:
        pass
    
    print("⚠️  Poppler may not be installed")
    print("   Install it with: brew install poppler (macOS)")
    print("   or: sudo apt-get install poppler-utils (Linux)")
    return False

def check_data_folder():
    """Check if Data folder exists and has PDFs"""
    import os
    data_folder = 'Data'
    if os.path.exists(data_folder):
        print(f"✅ Data folder exists")
        
        # Count PDF files
        pdf_count = 0
        for root, dirs, files in os.walk(data_folder):
            pdf_count += len([f for f in files if f.endswith('.pdf')])
        
        if pdf_count > 0:
            print(f"✅ Found {pdf_count} PDF file(s)")
            return True
        else:
            print("⚠️  No PDF files found in Data folder")
            return False
    else:
        print(f"❌ Data folder does not exist")
        return False

def main():
    print("=" * 50)
    print("PDF Search System - Setup Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_packages),
        ("Tesseract OCR", check_tesseract),
        ("Poppler", check_poppler),
        ("Data Folder", check_data_folder)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        results.append(check_func())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All checks passed! You're ready to run the application.")
        print("\nTo start the server, run:")
        print("  python app.py")
    else:
        print("⚠️  Some checks failed. Please install missing dependencies.")
        print("See README.md for detailed installation instructions.")
    print("=" * 50)

if __name__ == '__main__':
    main()

