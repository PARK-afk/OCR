# =============================================================================
# 간단한 OCR (광학 문자 인식) 프로그램
# 이미지와 PDF 파일에서 텍스트를 추출하는 GUI 애플리케이션
# 작성자: 사용자
# 주요 기능: 이미지 OCR, PDF OCR, 이미지 전처리, 결과 저장
# =============================================================================

# 🎯 클론 코딩 체크리스트 매핑
# =====================================
# STEP 1-2: 프로젝트 초기화 & 기본 윈도우 → Line 9-23 (imports), Line 28-42 (__init__)
# STEP 3: SimpleOCR 클래스 생성 → Line 25-42 (class 정의 및 초기화)
# STEP 4: 탭 구조 구현 → Line 44-73 (setup_ui, notebook), Line 75+ (탭 생성)
# STEP 5: 이미지 로드 기능 → Line 228+ (load_image, display_pil_image)
# STEP 6: 이미지 표시 기능 → Line 246+ (display_pil_image 구현)
# STEP 7: 이미지 전처리 기능 → Line 272+ (sharpen_image, enhance_contrast)
# STEP 8-9: OCR 엔진 연동 → Line 316+ (run_image_ocr)
# STEP 10: 결과 저장 → Line 450+ (save_result, save_pdf_result)
# STEP 11-12: PDF 처리 → Line 348+ (load_pdf, run_pdf_ocr, _process_pdf)
# STEP 13: 진행률 표시 → Line 394+ (_process_pdf 내부 진행률 바)
# STEP 14: 에러 처리 → Line 515+ (main 함수 try-catch)
# =====================================

# ★★★ STEP 1-2: 프로젝트 초기화 & 기본 윈도우 생성 ★★★
# Tkinter 경고 메시지 숨기기 (macOS 호환성)
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# GUI 라이브러리 - 사용자 인터페이스 생성을 위한 tkinter 모듈
import tkinter as tk
# tkinter 추가 위젯들 - ttk(테마 위젯), filedialog(파일선택), messagebox(메시지박스), scrolledtext(스크롤 텍스트)
from tkinter import ttk, filedialog, messagebox, scrolledtext
# OCR 엔진 - Tesseract OCR을 파이썬에서 사용할 수 있게 해주는 라이브러리
import pytesseract
# 이미지 처리 라이브러리 - Image(이미지 로드/처리), ImageTk(tkinter용 이미지), ImageFilter(필터), ImageEnhance(향상)
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
# PDF 처리 라이브러리 - PyMuPDF 라이브러리로 PDF를 이미지로 변환
import fitz  # PyMuPDF
# 입출력 스트림 처리를 위한 라이브러리
import io
# 멀티스레딩을 위한 라이브러리 - PDF 처리를 백그라운드에서 실행
import threading
# 날짜/시간 처리를 위한 라이브러리 (현재 코드에서는 사용하지 않음)
from datetime import datetime

# ★★★ STEP 3: SimpleOCR 클래스 생성 ★★★
# OCR 애플리케이션의 메인 클래스 정의
class SimpleOCR:
    # ★★★ STEP 3-1: 클래스 초기화 ★★★
    # 클래스 초기화 메서드 - 프로그램 시작시 호출됨
    def __init__(self, root):
        # tkinter 루트 윈도우 객체 저장
        self.root = root
        # 프로그램 창 제목 설정
        self.root.title("간단한 OCR 프로그램 (OpenCV 없음)")
        # 프로그램 창 크기 설정 (가로 1000픽셀, 세로 700픽셀)
        self.root.geometry("1000x700")

        # 현재 로드된 이미지를 저장할 변수 (초기값 None)
        self.current_image = None
        # PIL 이미지 객체를 저장할 변수 (초기값 None)
        self.current_pil_image = None

        # 사용자 인터페이스 설정 메서드 호출
        self.setup_ui()

    # ★★★ STEP 3-2: UI 설정 메서드 골격 ★★★
    # 전체 사용자 인터페이스 레이아웃 설정 메서드
    def setup_ui(self):
        # 그리드 가중치 설정을 먼저 설정하여 레이아웃 문제 방지
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 메인 프레임 생성 - 전체 레이아웃의 기본 컨테이너, 안쪽 여백 10픽셀
        main_frame = ttk.Frame(self.root, padding="10")
        # 메인 프레임을 루트 윈도우에 배치 (0행 0열, 모든 방향으로 확장)
        main_frame.pack(fill='both', expand=True)

        # ★★★ STEP 4-1: 노트북(탭) 컨트롤 생성 ★★★
        # 탭 컨트롤 생성 - 이미지 OCR과 PDF OCR 탭을 관리
        self.notebook = ttk.Notebook(main_frame)
        # 탭 컨트롤을 메인 프레임에 배치 (pack을 사용하여 더 안정적인 레이아웃)
        self.notebook.pack(fill='both', expand=True)

        # 각각의 탭들 생성 메서드 호출
        # 이미지 OCR 탭 설정 메서드 호출
        self.setup_image_tab()
        # PDF OCR 탭 설정 메서드 호출
        self.setup_pdf_tab()

        # 위젯들이 생성된 후 강제로 GUI 업데이트
        self.root.update_idletasks()
        self.root.update()

    # ★★★ STEP 4-2: 이미지 탭 생성 ★★★
    # 이미지 OCR 탭의 레이아웃과 기능들을 설정하는 메서드
    def setup_image_tab(self):
        """이미지 OCR 탭 생성 및 설정"""
        # 이미지 OCR용 탭 프레임 생성
        self.image_frame = ttk.Frame(self.notebook)
        # 생성된 프레임을 노트북에 '이미지 OCR'이라는 이름으로 추가
        self.notebook.add(self.image_frame, text="이미지 OCR")

        # 수평 컨테이너 생성 (왼쪽, 오른쪽 영역을 나란히 배치)
        main_container = ttk.Frame(self.image_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # 왼쪽 영역: 이미지 로드 및 미리보기를 위한 프레임 (레이블과 테두리 포함)
        left_frame = ttk.LabelFrame(main_container, text="이미지", padding="10")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0,5))

        # 이미지를 표시할 캔버스 생성 (400x400 픽셀, 흰색 배경)
        self.image_canvas = tk.Canvas(left_frame, width=400, height=400, bg='white')
        self.image_canvas.pack(pady=5)

        # 버튼들을 위한 프레임
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=5)

        # 이미지 관련 버튼들 생성 및 배치
        ttk.Button(button_frame, text="이미지 불러오기",
                  command=self.load_image).pack(side='left', padx=2)
        ttk.Button(button_frame, text="선명하게",
                  command=self.sharpen_image).pack(side='left', padx=2)
        ttk.Button(button_frame, text="대비 강화",
                  command=self.enhance_contrast).pack(side='left', padx=2)

        # 오른쪽 영역: OCR 결과 표시를 위한 프레임
        right_frame = ttk.LabelFrame(main_container, text="OCR 결과", padding="10")
        right_frame.pack(side='left', fill='both', expand=True, padx=(5,0))

        # 언어 선택 영역을 위한 서브 프레임
        lang_frame = ttk.Frame(right_frame)
        lang_frame.pack(pady=5)

        # "언어:" 레이블과 콤보박스
        ttk.Label(lang_frame, text="언어:").pack(side='left', padx=2)
        self.language_var = tk.StringVar(value="kor+eng")
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                          values=['kor+eng', 'kor', 'eng', 'chi_sim', 'jpn'])
        self.language_combo.pack(side='left', padx=2)

        # "OCR 실행" 버튼
        ttk.Button(right_frame, text="OCR 실행",
                  command=self.run_image_ocr).pack(pady=5)

        # OCR 결과를 표시할 스크롤 가능한 텍스트 영역
        self.image_result_text = scrolledtext.ScrolledText(right_frame, width=50, height=20)
        self.image_result_text.pack(fill='both', expand=True, pady=5)

        # "결과 저장" 버튼
        ttk.Button(right_frame, text="결과 저장",
                  command=self.save_result).pack(pady=5)

    # ★★★ STEP 4-3: PDF 탭 생성 ★★★
    # PDF OCR 탭의 레이아웃과 기능들을 설정하는 메서드
    def setup_pdf_tab(self):
        """PDF OCR 탭 생성 및 설정"""
        # PDF OCR용 탭 프레임 생성
        self.pdf_frame = ttk.Frame(self.notebook)
        # 생성된 프레임을 노트북에 'PDF OCR'이라는 이름으로 추가
        self.notebook.add(self.pdf_frame, text="PDF OCR")

        # PDF 파일 선택 영역을 위한 프레임 (레이블과 테두리 포함)
        file_frame = ttk.LabelFrame(self.pdf_frame, text="PDF 파일", padding="10")
        file_frame.pack(fill='x', padx=5, pady=5)

        # 파일 선택 영역
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill='x', pady=2)

        self.pdf_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.pdf_path_var, width=60).pack(side='left', fill='x', expand=True, padx=(0,5))
        ttk.Button(file_select_frame, text="찾아보기",
                  command=self.load_pdf).pack(side='right')

        # 페이지 범위 선택을 위한 서브 프레임
        page_frame = ttk.Frame(file_frame)
        page_frame.pack(pady=5)

        # 페이지 선택 위젯들
        ttk.Label(page_frame, text="페이지:").pack(side='left', padx=2)
        self.start_page_var = tk.StringVar(value="1")
        ttk.Entry(page_frame, textvariable=self.start_page_var, width=5).pack(side='left', padx=2)
        ttk.Label(page_frame, text="~").pack(side='left', padx=2)
        self.end_page_var = tk.StringVar(value="1")
        ttk.Entry(page_frame, textvariable=self.end_page_var, width=5).pack(side='left', padx=2)
        ttk.Button(page_frame, text="PDF OCR 실행",
                  command=self.run_pdf_ocr).pack(side='left', padx=10)

        # PDF 처리 진행률을 표시할 프로그레스 바
        self.pdf_progress = ttk.Progressbar(file_frame, mode='determinate')
        self.pdf_progress.pack(fill='x', pady=5)

        # PDF OCR 결과 표시를 위한 프레임 (레이블과 테두리 포함)
        result_frame = ttk.LabelFrame(self.pdf_frame, text="PDF OCR 결과", padding="10")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # PDF OCR 결과를 표시할 스크롤 가능한 텍스트 영역
        self.pdf_result_text = scrolledtext.ScrolledText(result_frame, width=80, height=25)
        self.pdf_result_text.pack(fill='both', expand=True, pady=(0,5))

        # "결과 저장" 버튼
        ttk.Button(result_frame, text="결과 저장",
                  command=self.save_pdf_result).pack(pady=5)

    # 이미지 파일을 로드하는 메서드
    def load_image(self):
        """이미지 파일 불러오기"""
        # 파일 선택 대화상자 열기 (이미지 파일만 필터링)
        file_path = filedialog.askopenfilename(
            title="이미지 선택",  # 대화상자 제목
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif")]  # 지원 파일 형식
        )

        # 사용자가 파일을 선택했는지 확인
        if file_path:
            try:
                # PIL을 사용하여 선택된 이미지 파일 로드
                self.current_pil_image = Image.open(file_path)
                # 로드된 이미지를 캔버스에 표시
                self.display_pil_image(self.current_pil_image)
            except Exception as e:
                # 이미지 로드 실패 시 오류 메시지 표시
                messagebox.showerror("오류", f"이미지 로드 실패: {str(e)}")

    # PIL 이미지를 tkinter 캔버스에 표시하는 메서드
    def display_pil_image(self, pil_image):
        """PIL 이미지를 캔버스에 표시"""
        # 이미지가 None인 경우 함수 종료
        if pil_image is None:
            return

        # 캔버스 크기 상수 정의
        canvas_width = 400   # 캔버스 가로 크기
        canvas_height = 400  # 캔버스 세로 크기

        # 이미지를 캔버스 크기에 맞게 비율 유지하면서 리사이즈
        # LANCZOS 알고리즘을 사용하여 고품질 리샘플링
        pil_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

        # PIL 이미지를 tkinter에서 사용할 수 있는 PhotoImage 형태로 변환
        photo = ImageTk.PhotoImage(pil_image)
        # 캔버스의 기존 내용을 모두 삭제
        self.image_canvas.delete("all")
        # 이미지를 캔버스 중앙에 표시 (중심점을 캔버스의 중앙으로 설정)
        self.image_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
        # 이미지 객체의 참조를 유지 (가비지 컬렉션 방지)
        self.image_canvas.image = photo

    # 이미지 선명도를 향상시키는 메서드
    # ★★★ STEP 7-1: 이미지 선명도 향상 ★★★
    def sharpen_image(self):
        """이미지 선명하게 만들기"""
        # 현재 로드된 이미지가 있는지 확인
        if self.current_pil_image is None:
            # 이미지가 없으면 경고 메시지 표시
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return

        try:
            # PIL의 ImageFilter.SHARPEN 필터를 적용하여 이미지 선명도 향상
            sharpened = self.current_pil_image.filter(ImageFilter.SHARPEN)
            # 선명하게 처리된 이미지로 현재 이미지 교체
            self.current_pil_image = sharpened
            # 처리된 이미지를 캔버스에 표시
            self.display_pil_image(self.current_pil_image)

        except Exception as e:
            # 선명도 처리 실패 시 오류 메시지 표시
            messagebox.showerror("오류", f"선명도 처리 실패: {str(e)}")

    # 이미지 대비를 강화하는 메서드
    # ★★★ STEP 7-2: 이미지 대비 강화 ★★★
    def enhance_contrast(self):
        """이미지 대비 강화"""
        # 현재 로드된 이미지가 있는지 확인
        if self.current_pil_image is None:
            # 이미지가 없으면 경고 메시지 표시
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return

        try:
            # PIL의 ImageEnhance.Contrast를 사용하여 대비 조정 객체 생성
            enhancer = ImageEnhance.Contrast(self.current_pil_image)
            # 대비를 2.0배로 강화 (1.0이 원본, 2.0이 2배 강화)
            enhanced = enhancer.enhance(2.0)
            # 대비가 강화된 이미지로 현재 이미지 교체
            self.current_pil_image = enhanced
            # 처리된 이미지를 캔버스에 표시
            self.display_pil_image(self.current_pil_image)

        except Exception as e:
            # 대비 강화 실패 시 오류 메시지 표시
            messagebox.showerror("오류", f"대비 강화 실패: {str(e)}")

    # 이미지에서 OCR을 실행하는 메서드
    # ★★★ STEP 8-9: OCR 엔진 연동 ★★★
    def run_image_ocr(self):
        """이미지 OCR 실행"""
        # 현재 로드된 이미지가 있는지 확인
        if self.current_pil_image is None:
            # 이미지가 없으면 경고 메시지 표시
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return

        try:
            # 사용자가 선택한 OCR 언어 가져오기
            language = self.language_var.get()
            # pytesseract를 사용하여 이미지에서 텍스트 추출
            text = pytesseract.image_to_string(self.current_pil_image, lang=language)

            # 결과 텍스트 영역의 기존 내용 삭제 (처음부터 끝까지)
            self.image_result_text.delete(1.0, tk.END)
            # 추출된 텍스트를 결과 영역에 삽입
            self.image_result_text.insert(1.0, text)

            # 추출된 텍스트가 있는지 확인 (공백 제거 후)
            if text.strip():
                # 텍스트가 인식되면 완료 메시지 표시
                messagebox.showinfo("완료", "OCR이 완료되었습니다!")
            else:
                # 텍스트가 인식되지 않으면 경고 메시지 표시
                messagebox.showwarning("결과", "인식된 텍스트가 없습니다.")

        except Exception as e:
            # OCR 실행 실패 시 오류 메시지 표시
            messagebox.showerror("오류", f"OCR 실행 실패: {str(e)}")

    # PDF 파일을 로드하는 메서드
    # ★★★ STEP 11-1: PDF 파일 선택 ★★★
    def load_pdf(self):
        """PDF 파일 불러오기"""
        # PDF 파일 선택 대화상자 열기
        file_path = filedialog.askopenfilename(
            title="PDF 선택",  # 대화상자 제목
            filetypes=[("PDF 파일", "*.pdf")]  # PDF 파일만 필터링
        )

        # 사용자가 파일을 선택했는지 확인
        if file_path:
            # 선택된 PDF 파일 경로를 변수에 저장
            self.pdf_path_var.set(file_path)

    # PDF OCR을 실행하는 메서드 (메인 스레드에서 실행)
    # ★★★ STEP 12: PDF to Image 변환 ★★★
    def run_pdf_ocr(self):
        """PDF OCR 실행"""
        # 선택된 PDF 파일 경로 가져오기
        pdf_path = self.pdf_path_var.get()
        # PDF 파일이 선택되었는지 확인
        if not pdf_path:
            # PDF 파일이 선택되지 않았으면 경고 메시지 표시
            messagebox.showwarning("경고", "PDF 파일을 선택해주세요.")
            return

        try:
            # 시작 페이지를 정수로 변환 (사용자 입력은 1부터 시작하므로 -1)
            start_page = int(self.start_page_var.get()) - 1  # 0-based index
            # 끝 페이지를 정수로 변환 (사용자 입력은 1부터 시작하므로 -1)
            end_page = int(self.end_page_var.get()) - 1
        except ValueError:
            # 페이지 번호가 유효하지 않으면 오류 메시지 표시
            messagebox.showerror("오류", "올바른 페이지 번호를 입력해주세요.")
            return

        # PDF 처리를 백그라운드 스레드에서 실행 (UI 블로킹 방지)
        thread = threading.Thread(target=self._process_pdf, args=(pdf_path, start_page, end_page))
        # 데몬 스레드로 설정 (메인 프로그램 종료시 함께 종료)
        thread.daemon = True
        # 스레드 시작
        thread.start()

    # PDF를 실제로 처리하는 메서드 (백그라운드 스레드에서 실행)
    # ★★★ STEP 13: 진행률 표시 ★★★
    def _process_pdf(self, pdf_path, start_page, end_page):
        """PDF 처리 (백그라운드)"""
        try:
            # PyMuPDF를 사용하여 PDF 문서 열기
            doc = fitz.open(pdf_path)
            # 처리할 총 페이지 수 계산 (끝 페이지+1과 문서 총 페이지 중 작은 값)
            total_pages = min(end_page + 1, len(doc))

            # 프로그레스 바의 최대값을 처리할 페이지 수로 설정
            self.pdf_progress.config(maximum=total_pages - start_page)

            # 추출된 텍스트를 저장할 리스트
            all_text = []

            # 지정된 범위의 각 페이지에 대해 처리
            for page_num in range(start_page, total_pages):
                # 현재 페이지 객체 가져오기
                page = doc[page_num]

                # 페이지를 이미지로 변환 (2x 해상도로 품질 향상)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                # 픽셀맵을 PNG 바이트 데이터로 변환
                img_data = pix.tobytes("png")
                # 바이트 데이터를 PIL 이미지로 변환
                pil_image = Image.open(io.BytesIO(img_data))

                # 사용자가 선택한 OCR 언어 가져오기
                language = self.language_var.get()
                # pytesseract를 사용하여 페이지 이미지에서 텍스트 추출
                text = pytesseract.image_to_string(pil_image, lang=language)

                # 페이지 번호와 함께 추출된 텍스트를 리스트에 추가
                all_text.append(f"=== 페이지 {page_num + 1} ===\n{text}\n")

                # 진행률 바 업데이트 (현재 처리된 페이지 수)
                self.pdf_progress.config(value=page_num - start_page + 1)
                # GUI 업데이트 강제 실행 (백그라운드 스레드에서 UI 업데이트)
                self.root.update()

            # PDF 문서 닫기 (메모리 해제)
            doc.close()

            # 모든 페이지의 텍스트를 하나로 합치기
            result_text = '\n'.join(all_text)
            # 결과 텍스트 영역의 기존 내용 삭제
            self.pdf_result_text.delete(1.0, tk.END)
            # 추출된 모든 텍스트를 결과 영역에 삽입
            self.pdf_result_text.insert(1.0, result_text)

            # 처리 완료 메시지 표시 (처리된 페이지 수 포함)
            messagebox.showinfo("완료", f"PDF OCR이 완료되었습니다. ({total_pages - start_page}페이지 처리)")

        except Exception as e:
            # PDF 처리 실패 시 오류 메시지 표시
            messagebox.showerror("오류", f"PDF 처리 실패: {str(e)}")
        finally:
            # 처리 완료 후 진행률 바를 0으로 리셋
            self.pdf_progress.config(value=0)

    # 이미지 OCR 결과를 파일로 저장하는 메서드
    # ★★★ STEP 10: 결과 저장 ★★★
    def save_result(self):
        """OCR 결과 저장"""
        # 결과 텍스트 영역에서 모든 텍스트를 가져오고 앞뒤 공백 제거
        text = self.image_result_text.get(1.0, tk.END).strip()
        # 저장할 텍스트가 있는지 확인
        if not text:
            # 텍스트가 없으면 경고 메시지 표시
            messagebox.showwarning("경고", "저장할 텍스트가 없습니다.")
            return

        # 파일 저장 대화상자 열기
        file_path = filedialog.asksaveasfilename(
            title="결과 저장",  # 대화상자 제목
            defaultextension=".txt",  # 기본 확장자
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]  # 파일 형식 필터
        )

        # 사용자가 저장 경로를 지정했는지 확인
        if file_path:
            try:
                # UTF-8 인코딩으로 텍스트 파일 쓰기
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                # 저장 완료 메시지 표시
                messagebox.showinfo("완료", "결과가 저장되었습니다.")
            except Exception as e:
                # 파일 저장 실패 시 오류 메시지 표시
                messagebox.showerror("오류", f"저장 실패: {str(e)}")

    # PDF OCR 결과를 파일로 저장하는 메서드
    # ★★★ STEP 10: PDF 결과 저장 ★★★
    def save_pdf_result(self):
        """PDF OCR 결과 저장"""
        # PDF 결과 텍스트 영역에서 모든 텍스트를 가져오고 앞뒤 공백 제거
        text = self.pdf_result_text.get(1.0, tk.END).strip()
        # 저장할 텍스트가 있는지 확인
        if not text:
            # 텍스트가 없으면 경고 메시지 표시
            messagebox.showwarning("경고", "저장할 텍스트가 없습니다.")
            return

        # PDF 결과 저장을 위한 파일 저장 대화상자 열기
        file_path = filedialog.asksaveasfilename(
            title="PDF OCR 결과 저장",  # 대화상자 제목
            defaultextension=".txt",  # 기본 확장자
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]  # 파일 형식 필터
        )

        # 사용자가 저장 경로를 지정했는지 확인
        if file_path:
            try:
                # UTF-8 인코딩으로 텍스트 파일 쓰기
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                # 저장 완료 메시지 표시
                messagebox.showinfo("완료", "PDF OCR 결과가 저장되었습니다.")
            except Exception as e:
                # 파일 저장 실패 시 오류 메시지 표시
                messagebox.showerror("오류", f"저장 실패: {str(e)}")

# ★★★ STEP 14: 에러 처리 및 최종 통합 ★★★
# 프로그램의 메인 함수
def main():
    try:
        # tkinter 루트 윈도우 생성
        root = tk.Tk()
        # SimpleOCR 애플리케이션 객체 생성
        app = SimpleOCR(root)
        # GUI 이벤트 루프 시작 (사용자 상호작용 대기)
        root.mainloop()
    except Exception as e:
        # 프로그램 실행 중 오류 발생 시 콘솔에 오류 정보 출력
        print(f"오류 발생: {e}")
        # 상세한 오류 추적 정보 출력 (디버깅용)
        import traceback
        traceback.print_exc()

# 스크립트가 직접 실행될 때만 main() 함수 호출
# (다른 모듈에서 import 될 때는 실행되지 않음)
if __name__ == "__main__":
    main()