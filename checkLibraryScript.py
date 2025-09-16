# 간단한 라이브러리 설치 확인
import sys

print("파이썬 버전:", sys.version)
print("\n=== 라이브러리 확인 중... ===\n")

# 1. tkinter 확인
try:
    import tkinter
    print("✅ tkinter - OK")
except ImportError:
    print("❌ tkinter - 설치 필요")

# 2. PIL (Pillow) 확인
try:
    from PIL import Image
    print("✅ Pillow (PIL) - OK")
except ImportError:
    print("❌ Pillow - 설치 필요: pip install pillow")

# 3. OpenCV 확인
try:
    import cv2
    print("✅ OpenCV - OK")
except ImportError:
    print("❌ OpenCV - 설치 필요: pip install opencv-python")

# 4. numpy 확인 (OpenCV 의존성)
try:
    import numpy
    print("✅ NumPy - OK")
except ImportError:
    print("❌ NumPy - 설치 필요: pip install numpy")

# 5. PyMuPDF 확인
try:
    import fitz
    print("✅ PyMuPDF - OK")
except ImportError:
    print("❌ PyMuPDF - 설치 필요: pip install PyMuPDF")

# 6. pytesseract 확인
try:
    import pytesseract
    print("✅ pytesseract - OK")
    
    # Tesseract 엔진 확인
    try:
        version = pytesseract.get_tesseract_version()
        print(f"   Tesseract 버전: {version}")
        
        # 언어 확인
        languages = pytesseract.get_languages()
        print(f"   지원 언어: {languages}")
        
        if 'kor' in languages:
            print("   ✅ 한국어 지원")
        else:
            print("   ⚠️ 한국어 미지원 - 언어팩 설치 필요")
            
    except Exception as e:
        print(f"   ⚠️ Tesseract 엔진 오류: {e}")
        print("   Tesseract OCR 엔진을 설치하세요")
        
except ImportError:
    print("❌ pytesseract - 설치 필요: pip install pytesseract")

print("\n=== 확인 완료 ===")