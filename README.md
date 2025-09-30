# OCR 프로그램

이미지와 PDF 파일에서 텍스트를 추출하는 GUI 기반 OCR(광학 문자 인식) 애플리케이션입니다.

## 주요 기능

- **이미지 OCR**: PNG, JPG, JPEG, BMP, TIFF, GIF 형식의 이미지 파일에서 텍스트 추출
- **PDF OCR**: PDF 파일의 특정 페이지 범위에서 텍스트 추출
- **이미지 전처리**: 선명도 조정 및 대비 강화 기능
- **다국어 지원**: 한국어, 영어, 중국어(간체), 일본어 등
- **결과 저장**: 추출된 텍스트를 텍스트 파일로 저장

## 필요 환경

- Python 3.x
- Tesseract OCR 엔진

## 설치 방법

### 1. Tesseract OCR 설치

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # 다국어 지원
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kor  # 한국어 지원
```

**Windows:**
[Tesseract 공식 다운로드 페이지](https://github.com/UB-Mannheim/tesseract/wiki)에서 설치

### 2. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성
python3 -m venv ocr_env

# 가상환경 활성화
source ocr_env/bin/activate  # macOS/Linux
# 또는
ocr_env\Scripts\activate  # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
```

## 실행 방법

### 방법 1: 셸 스크립트 사용 (macOS/Linux)

```bash
./run_ocr.sh
```

### 방법 2: 직접 실행

```bash
# 가상환경 활성화
source ocr_env/bin/activate

# 프로그램 실행
python new.py
```

## 사용 방법

### 이미지 OCR

1. "이미지 OCR" 탭 선택
2. "이미지 불러오기" 버튼 클릭하여 이미지 파일 선택
3. 필요시 "선명하게" 또는 "대비 강화" 버튼으로 이미지 전처리
4. 언어 선택 (기본값: 한국어+영어)
5. "OCR 실행" 버튼 클릭
6. 결과 확인 후 "결과 저장" 버튼으로 텍스트 파일 저장

### PDF OCR

1. "PDF OCR" 탭 선택
2. "찾아보기" 버튼 클릭하여 PDF 파일 선택
3. 처리할 페이지 범위 입력 (예: 1 ~ 5)
4. "PDF OCR 실행" 버튼 클릭
5. 진행률 바를 통해 처리 상태 확인
6. 결과 확인 후 "결과 저장" 버튼으로 텍스트 파일 저장

## 지원 언어

- `kor+eng`: 한국어 + 영어 (기본값)
- `kor`: 한국어
- `eng`: 영어
- `chi_sim`: 중국어(간체)
- `jpn`: 일본어

## 파일 구조

```
OCR/
├── new.py              # 메인 애플리케이션 파일
├── run_ocr.sh          # 실행 스크립트
├── requirements.txt    # Python 의존성 패키지 목록
├── runtime.txt         # Python 버전 정보
├── ocr_env/            # Python 가상환경 디렉토리
└── README.md           # 프로젝트 문서
```

## 의존성 패키지

- `pytesseract`: Tesseract OCR 파이썬 래퍼
- `Pillow`: 이미지 처리 라이브러리
- `PyMuPDF (fitz)`: PDF 처리 라이브러리

## 문제 해결

### Tesseract를 찾을 수 없다는 오류가 발생하는 경우

`new.py` 파일에 Tesseract 실행 파일 경로를 직접 지정:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # macOS/Linux
# 또는
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
```

### 특정 언어가 인식되지 않는 경우

해당 언어 데이터가 설치되어 있는지 확인:

```bash
# macOS
brew install tesseract-lang

# Linux
sudo apt-get install tesseract-ocr-[언어코드]
```

## 라이선스

이 프로젝트는 개인 학습 및 사용 목적으로 작성되었습니다.

## 기여

버그 리포트 및 개선 제안은 이슈를 통해 제출해 주세요.