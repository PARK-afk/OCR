#!/bin/bash

# 완전한 OCR 프로그램 환경 마이그레이션 스크립트
# Python 버전까지 포함한 완전한 환경 복제

echo "=== 완전한 OCR 환경 마이그레이션 시작 ==="

# 운영체제 확인
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac
echo "감지된 OS: $MACHINE"

# Python 3.9.6 설치 (pyenv 사용)
echo "1. Python 3.9.6 설치 확인/설치..."
if command -v pyenv >/dev/null 2>&1; then
    echo "pyenv 감지됨"
    if pyenv versions | grep -q "3.9.6"; then
        echo "✅ Python 3.9.6 이미 설치됨"
    else
        echo "Python 3.9.6 설치 중..."
        pyenv install 3.9.6
        pyenv local 3.9.6
    fi
else
    echo "⚠️ pyenv가 설치되어 있지 않습니다."
    echo "현재 Python 버전: $(python --version)"
    echo "Python 3.9.6 사용을 권장합니다."
fi

# Tesseract 자동 설치
echo "2. Tesseract OCR 자동 설치..."
if command -v tesseract >/dev/null 2>&1; then
    echo "✅ Tesseract 이미 설치됨: $(tesseract --version | head -1)"
else
    if [[ "$MACHINE" == "Mac" ]]; then
        echo "macOS에서 Tesseract 설치 중..."
        if command -v brew >/dev/null 2>&1; then
            brew install tesseract tesseract-lang
        else
            echo "❌ Homebrew가 설치되어 있지 않습니다."
            echo "수동으로 설치해주세요: brew install tesseract tesseract-lang"
        fi
    elif [[ "$MACHINE" == "Linux" ]]; then
        echo "Linux에서 Tesseract 설치 중..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-kor tesseract-ocr-eng
    fi
fi

# 가상환경 생성 (강제)
echo "3. 전용 가상환경 생성..."
if [[ -d "ocr_env" ]]; then
    echo "기존 가상환경 삭제 중..."
    rm -rf ocr_env
fi

python -m venv ocr_env
source ocr_env/bin/activate

# 정확한 버전으로 라이브러리 설치
echo "4. 정확한 버전의 라이브러리 설치..."
pip install --upgrade pip==23.3.1  # pip 버전도 고정

# 정확한 버전으로 강제 설치
pip install pytesseract==0.3.13
pip install Pillow==11.3.0
pip install PyMuPDF==1.26.4
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78

# 버전 확인 및 출력
echo "5. 설치된 버전 확인..."
python -c "
import sys
import pytesseract
import PIL
import fitz
import numpy
import cv2

print('🐍 Python 버전:', sys.version)
print('📸 pytesseract 버전:', pytesseract.__version__)
print('🖼️ Pillow 버전:', PIL.__version__)
print('📄 PyMuPDF 버전:', fitz.version)
print('🔢 NumPy 버전:', numpy.__version__)
print('👁️ OpenCV 버전:', cv2.__version__)

try:
    tesseract_version = pytesseract.get_tesseract_version()
    print('⚙️ Tesseract 엔진:', tesseract_version)

    languages = pytesseract.get_languages()
    print('🌍 지원 언어:', len(languages), '개')
    if 'kor' in languages:
        print('✅ 한국어 지원됨')
    else:
        print('❌ 한국어 미지원')
except Exception as e:
    print('⚠️ Tesseract 연결 실패:', e)
"

echo ""
echo "=== 완전한 환경 마이그레이션 완료 ==="
echo ""
echo "📌 사용법:"
echo "1. 가상환경 활성화: source ocr_env/bin/activate"
echo "2. 프로그램 실행: python testOCR.py"
echo "3. 가상환경 비활성화: deactivate"