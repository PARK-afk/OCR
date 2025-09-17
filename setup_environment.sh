#!/bin/bash

# OCR 프로그램 환경 설정 스크립트
# 사용법: chmod +x setup_environment.sh && ./setup_environment.sh

echo "=== OCR 프로그램 환경 설정 시작 ==="

# Python 버전 확인
echo "1. Python 버전 확인..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python이 설치되어 있지 않습니다."
    echo "Python 3.9.6 이상을 설치해주세요."
    exit 1
fi

# Tesseract 설치 확인 (macOS)
echo "2. Tesseract OCR 엔진 확인..."
if command -v tesseract >/dev/null 2>&1; then
    echo "✅ Tesseract 설치됨: $(tesseract --version | head -1)"
else
    echo "⚠️ Tesseract가 설치되어 있지 않습니다."
    echo "macOS에서 설치: brew install tesseract tesseract-lang"
    echo "계속 진행하시겠습니까? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 가상환경 생성 (선택사항)
echo "3. 가상환경을 생성하시겠습니까? (권장) (y/n)"
read -r create_venv
if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo "가상환경 생성 중..."
    python -m venv ocr_env
    echo "가상환경 활성화: source ocr_env/bin/activate"
    source ocr_env/bin/activate
fi

# 필수 라이브러리 설치
echo "4. Python 라이브러리 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 설치 확인
echo "5. 설치 확인..."
python -c "
import pytesseract
import PIL
import fitz
print('✅ 모든 라이브러리 설치 완료')
print('Tesseract 버전:', pytesseract.get_tesseract_version())
print('Pillow 버전:', PIL.__version__)
print('PyMuPDF 버전:', fitz.version)
"

echo ""
echo "=== 환경 설정 완료 ==="
echo "프로그램 실행: python testOCR.py"