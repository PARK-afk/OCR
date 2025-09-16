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
# 날짜/시간 처리를 위한 라이브러리
from datetime import datetime

# OCR 애플리케이션의 메인 클래스 정의
class SimpleOCR:
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
    
    # 전체 사용자 인터페이스 레이아웃 설정 메서드
    def setup_ui(self):
        # 메인 프레임 생성 - 전체 레이아웃의 기본 컴테이너, 안쪽 여백 10픽셀
        main_frame = ttk.Frame(self.root, padding="10")
        # 메인 프레임을 루트 윈도우에 배치 (0행 0열, 모든 방향으로 확장)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 탭 컨트롤 생성 - 이미지 OCR과 PDF OCR 탭을 관리
        self.notebook = ttk.Notebook(main_frame)
        # 탭 컨트롤을 메인 프레임에 배치 (0행 0열, 2열 폭, 모든 방향으로 확장)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 각각의 탭들 생성 메서드 호출
        # 이미지 OCR 탭 설정 메서드 호출
        self.setup_image_tab()
        # PDF OCR 탭 설정 메서드 호출
        self.setup_pdf_tab()

        # 그리드 가중치 설정 - 윈도우 크기 변경 시 자동 크기 조정
        # 루트 윈도우의 0번 열에 가중치 1 지정 (가로 확장)
        self.root.columnconfigure(0, weight=1)
        # 루트 윈도우의 0번 행에 가중치 1 지정 (세로 확장)
        self.root.rowconfigure(0, weight=1)
        # 메인 프레임의 0번 열에 가중치 1 지정
        main_frame.columnconfigure(0, weight=1)
        # 메인 프레임의 0번 행에 가중치 1 지정
        main_frame.rowconfigure(0, weight=1)
    
    # 이미지 OCR 탭의 레이아웃과 기능들을 설정하는 메서드
    def setup_image_tab(self):
        """이미지 OCR 탭 생성 및 설정"""
        # 이미지 OCR용 탭 프레임 생성
        self.image_frame = ttk.Frame(self.notebook)
        # 생성된 프레임을 노트북에 '이미진 OCR'이라는 이름으로 추가
        self.notebook.add(self.image_frame, text="이미지 OCR")

        # 왼쪽 영역: 이미지 로드 및 미리보기를 위한 프레임 (레이블과 테두리 포함)
        left_frame = ttk.LabelFrame(self.image_frame, text="이미지", padding="10")
        # 왼쪽 프레임을 이미지 탭에 배치 (0행 0열, 여백 5픽셀, 모든 방향 확장)
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 이미지를 표시할 캔버스 생성 (400x400 픽셀, 흰색 배경)
        self.image_canvas = tk.Canvas(left_frame, width=400, height=400, bg='white')
        # 캔버스를 왼쪽 프레임에 배치 (0행, 3열 폭, 세로 여백 5픽셀)
        self.image_canvas.grid(row=0, column=0, columnspan=3, pady=5)
        
        # 이미지 버튼들
        ttk.Button(left_frame, text="이미지 불러오기", 
                  command=self.load_image).grid(row=1, column=0, padx=2, pady=5)
        ttk.Button(left_frame, text="선명하게", 
                  command=self.sharpen_image).grid(row=1, column=1, padx=2, pady=5)
        ttk.Button(left_frame, text="대비 강화", 
                  command=self.enhance_contrast).grid(row=1, column=2, padx=2, pady=5)
        
        # 오른쪽 프레임 (결과)
        right_frame = ttk.LabelFrame(self.image_frame, text="OCR 결과", padding="10")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 언어 선택
        lang_frame = ttk.Frame(right_frame)
        lang_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(lang_frame, text="언어:").grid(row=0, column=0, padx=2)
        self.language_var = tk.StringVar(value="kor+eng")
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                          values=['kor+eng', 'kor', 'eng', 'chi_sim', 'jpn'])
        self.language_combo.grid(row=0, column=1, padx=2)
        
        # OCR 실행 버튼
        ttk.Button(right_frame, text="OCR 실행", 
                  command=self.run_image_ocr).grid(row=1, column=0, pady=5)
        
        # 결과 텍스트
        self.image_result_text = scrolledtext.ScrolledText(right_frame, width=50, height=20)
        self.image_result_text.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 저장 버튼
        ttk.Button(right_frame, text="결과 저장", 
                  command=self.save_result).grid(row=3, column=0, pady=5)
        
        # 그리드 가중치
        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.columnconfigure(1, weight=1)
        self.image_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(2, weight=1)
    
    def setup_pdf_tab(self):
        """PDF OCR 탭"""
        self.pdf_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pdf_frame, text="PDF OCR")
        
        # PDF 파일 선택
        file_frame = ttk.LabelFrame(self.pdf_frame, text="PDF 파일", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.pdf_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.pdf_path_var, width=60).grid(row=0, column=0, padx=2)
        ttk.Button(file_frame, text="찾아보기", 
                  command=self.load_pdf).grid(row=0, column=1, padx=2)
        
        # 페이지 선택
        page_frame = ttk.Frame(file_frame)
        page_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(page_frame, text="페이지:").grid(row=0, column=0, padx=2)
        self.start_page_var = tk.StringVar(value="1")
        ttk.Entry(page_frame, textvariable=self.start_page_var, width=5).grid(row=0, column=1, padx=2)
        ttk.Label(page_frame, text="~").grid(row=0, column=2, padx=2)
        self.end_page_var = tk.StringVar(value="1")
        ttk.Entry(page_frame, textvariable=self.end_page_var, width=5).grid(row=0, column=3, padx=2)
        
        ttk.Button(page_frame, text="PDF OCR 실행", 
                  command=self.run_pdf_ocr).grid(row=0, column=4, padx=10)
        
        # 진행률 표시
        self.pdf_progress = ttk.Progressbar(file_frame, mode='determinate')
        self.pdf_progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 결과 프레임
        result_frame = ttk.LabelFrame(self.pdf_frame, text="PDF OCR 결과", padding="10")
        result_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 결과 텍스트
        self.pdf_result_text = scrolledtext.ScrolledText(result_frame, width=80, height=25)
        self.pdf_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 저장 버튼
        ttk.Button(result_frame, text="결과 저장", 
                  command=self.save_pdf_result).grid(row=1, column=0, pady=5)
        
        # 그리드 가중치
        self.pdf_frame.columnconfigure(0, weight=1)
        self.pdf_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def load_image(self):
        """이미지 파일 불러오기"""
        file_path = filedialog.askopenfilename(
            title="이미지 선택",
            filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif")]
        )
        
        if file_path:
            try:
                # PIL로 이미지 로드
                self.current_pil_image = Image.open(file_path)
                self.display_pil_image(self.current_pil_image)
            except Exception as e:
                messagebox.showerror("오류", f"이미지 로드 실패: {str(e)}")
    
    def display_pil_image(self, pil_image):
        """PIL 이미지를 캔버스에 표시"""
        if pil_image is None:
            return
        
        # 이미지 크기 조정
        canvas_width = 400
        canvas_height = 400
        
        # 비율 유지하면서 리사이즈
        pil_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # 이미지를 캔버스 중앙에 표시
        photo = ImageTk.PhotoImage(pil_image)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
        self.image_canvas.image = photo  # 참조 유지
    
    def sharpen_image(self):
        """이미지 선명하게 만들기"""
        if self.current_pil_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return
        
        try:
            # 선명도 필터 적용
            sharpened = self.current_pil_image.filter(ImageFilter.SHARPEN)
            self.current_pil_image = sharpened
            self.display_pil_image(self.current_pil_image)
            
        except Exception as e:
            messagebox.showerror("오류", f"선명도 처리 실패: {str(e)}")
    
    def enhance_contrast(self):
        """이미지 대비 강화"""
        if self.current_pil_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return
        
        try:
            # 대비 강화
            enhancer = ImageEnhance.Contrast(self.current_pil_image)
            enhanced = enhancer.enhance(2.0)  # 2배 대비 강화
            self.current_pil_image = enhanced
            self.display_pil_image(self.current_pil_image)
            
        except Exception as e:
            messagebox.showerror("오류", f"대비 강화 실패: {str(e)}")
    
    def run_image_ocr(self):
        """이미지 OCR 실행"""
        if self.current_pil_image is None:
            messagebox.showwarning("경고", "먼저 이미지를 불러와주세요.")
            return
        
        try:
            # OCR 실행
            language = self.language_var.get()
            text = pytesseract.image_to_string(self.current_pil_image, lang=language)
            
            # 결과 표시
            self.image_result_text.delete(1.0, tk.END)
            self.image_result_text.insert(1.0, text)
            
            if text.strip():
                messagebox.showinfo("완료", "OCR이 완료되었습니다!")
            else:
                messagebox.showwarning("결과", "인식된 텍스트가 없습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"OCR 실행 실패: {str(e)}")
    
    def load_pdf(self):
        """PDF 파일 불러오기"""
        file_path = filedialog.askopenfilename(
            title="PDF 선택",
            filetypes=[("PDF 파일", "*.pdf")]
        )
        
        if file_path:
            self.pdf_path_var.set(file_path)
    
    def run_pdf_ocr(self):
        """PDF OCR 실행"""
        pdf_path = self.pdf_path_var.get()
        if not pdf_path:
            messagebox.showwarning("경고", "PDF 파일을 선택해주세요.")
            return
        
        try:
            start_page = int(self.start_page_var.get()) - 1  # 0-based index
            end_page = int(self.end_page_var.get()) - 1
        except ValueError:
            messagebox.showerror("오류", "올바른 페이지 번호를 입력해주세요.")
            return
        
        # 백그라운드에서 처리
        thread = threading.Thread(target=self._process_pdf, args=(pdf_path, start_page, end_page))
        thread.daemon = True
        thread.start()
    
    def _process_pdf(self, pdf_path, start_page, end_page):
        """PDF 처리 (백그라운드)"""
        try:
            doc = fitz.open(pdf_path)
            total_pages = min(end_page + 1, len(doc))
            
            self.pdf_progress.config(maximum=total_pages - start_page)
            
            all_text = []
            
            for page_num in range(start_page, total_pages):
                page = doc[page_num]
                
                # 페이지를 이미지로 변환
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x 해상도
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # OCR 실행
                language = self.language_var.get()
                text = pytesseract.image_to_string(pil_image, lang=language)
                
                all_text.append(f"=== 페이지 {page_num + 1} ===\n{text}\n")
                
                # 진행률 업데이트
                self.pdf_progress.config(value=page_num - start_page + 1)
                self.root.update()
            
            doc.close()
            
            # 결과 표시
            result_text = '\n'.join(all_text)
            self.pdf_result_text.delete(1.0, tk.END)
            self.pdf_result_text.insert(1.0, result_text)
            
            messagebox.showinfo("완료", f"PDF OCR이 완료되었습니다. ({total_pages - start_page}페이지 처리)")
            
        except Exception as e:
            messagebox.showerror("오류", f"PDF 처리 실패: {str(e)}")
        finally:
            self.pdf_progress.config(value=0)
    
    def save_result(self):
        """OCR 결과 저장"""
        text = self.image_result_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("경고", "저장할 텍스트가 없습니다.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="결과 저장",
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("완료", "결과가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {str(e)}")
    
    def save_pdf_result(self):
        """PDF OCR 결과 저장"""
        text = self.pdf_result_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("경고", "저장할 텍스트가 없습니다.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="PDF OCR 결과 저장",
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("완료", "PDF OCR 결과가 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = SimpleOCR(root)
        root.mainloop()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()