import os
import zipfile
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from weasyprint import HTML
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger

PRETENDARD_LINK = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css'
CUSTOM_CSS_LINK = 'https://d1gnhxw044igtr.cloudfront.net/notion_cv_style_px_12.css'

PATH_FINAL_HTML = './tmp/image_pdf.html'
PATH_TEMP_PDF = './tmp/image_pdf_final.pdf'
PATH_FINAL_PDF = './result/image_pdf_final.pdf'

# zip 파일로부터 html, image 가져옴
def find_html_and_assets(notion_dir):
    for root, dirs, files in os.walk(notion_dir):
        html_file = next((os.path.join(root, f) for f in files if f.endswith('.html')), None)
        if html_file:
            assets_dir = os.path.join(root)
            return html_file, assets_dir
    return None, None

def lambda_handler():
    file_path = './temp/cv_2'

    # 1. 테스트 파일 압축 해제
    with zipfile.ZipFile('test/cv_jihyun_2.zip', 'r') as zip_ref:
        zip_ref.extractall(file_path)

    # 2. HTML 파일과 에셋 디렉토리 찾기
    html_file, assets_dir = find_html_and_assets(file_path)

    if not html_file:
        return {
            'statusCode': 400,
            'body': 'HTML file not found in ZIP'
        }
    
    print('zip 파일 안에 html 파일 존재함')
    
    # 3. HTML 파일 읽음
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    print('soup에 담음')

    # 4. 기존 style 삭제
    for style in soup.find_all('style'):
        style.decompose()

    print('기존 스타일 삭제')

    # 5. font 넣기
    head = soup.find('head')
    font_link = soup.new_tag('link', rel='stylesheet', href=PRETENDARD_LINK)
    head.append(font_link)

    print('폰트 링크 추가')

    # 6. CSS 파일 link로 추가
    new_style_link = soup.new_tag('link', rel='stylesheet', href=CUSTOM_CSS_LINK)
    head.append(new_style_link)

    print('새로운 스타일 링크 추가')

    # 7. HTML 파일 저장 
    with open(PATH_FINAL_HTML, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print('HTML 파일 저장')

    # 8. HTML을 고해상도 PDF로 변환
    HTML(PATH_FINAL_HTML).write_pdf(PATH_TEMP_PDF, resolution=300)

    print('HTML TO PDF 저장')

    # 8. PDF를 이미지로 변환
    pages = convert_from_path(PATH_TEMP_PDF, 300)

    print('PDF 이미지 변환')

    # 9. OCR 처리 및 검색 가능한 PDF 생성
    page_files = []  # 생성된 페이지 파일들의 리스트를 저장 

    for i, page in enumerate(pages):
        output_file = f'tmp/page_{i}.pdf'
        page_files.append(output_file)
        
        # OCR 처리 - 한글과 영어 모두 처리
        text = pytesseract.image_to_pdf_or_hocr(
            page, 
            extension='pdf',
            lang='kor+eng'  # 한글과 영어 모두 인식
        )
        
        # 새 PDF 생성
        with open(output_file, 'wb') as f:
            f.write(text)

    print('페이지별 OCR')

    # 10. 모든 페이지 병합
    merger = PdfMerger()
    
    for pdf_file in page_files:
        merger.append(pdf_file)

    merger.write(PATH_FINAL_PDF)
    merger.close()

    print('PDF 병합 완료')
    
lambda_handler()