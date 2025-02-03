import os
import zipfile
from bs4 import BeautifulSoup
from typing import Dict, Any
from dotenv import load_dotenv

# Local Import
from function.extract_files_from_zip import extract_files_from_zip as extract_files
from function.convert_html_to_ocr_pdf import convert_html_to_ocr_pdf as convert_to_ocr_pdf
from function.s3 import download_zip, upload_pdf

load_dotenv() 

# CONSTANT
PRETENDARD_LINK = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css'
CUSTOM_CSS_LINK = os.getenv('CSS_PATH')

# s3
S3_BUCKET = os.getenv('S3_BUCKET')
LOCAL_TEMP_DIR = 'tmp/'




def lambda_handler(event: Dict[Any, Any], context: Any) -> Dict[str, Any]:
    try:
        # UUID 존재 및 유효성 체크
        if 'uuid' not in event or not event['uuid'] or not isinstance(event['uuid'], str):
            return {
                'statusCode': 400,
                'body': {
                    'message': '요청이 유효하지 않습니다.'
                }
            }
        
        request_uuid = event.get('requestId').strip() # 앞뒤 공백 제거
        input_key = f"temp/{request_uuid}/{request_uuid}.zip"
        output_key = f"temp/{request_uuid}/{request_uuid}.result.pdf"

        # 임시 로컬 파일 경로 설정
        temp_zip_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.zip")
        temp_extracted_files_path = os.path.join(LOCAL_TEMP_DIR, 'extracted/')
        temp_html_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.html")
        temp_pdf_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.pdf")
        
        # zip 파일 다운로드
        download_zip(S3_BUCKET, input_key, temp_zip_local_path)

        # 1. zip 파일 압축 해제
        with zipfile.ZipFile(temp_zip_local_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extracted_files_path)

        # 2. HTML 파일과 에셋 디렉토리 찾기
        html_file, image_files = extract_files(temp_extracted_files_path)

        if not html_file:
            return {
                'statusCode': 400,
                'body': 'HTML file not found in ZIP'
            }
        
        # 3. HTML 파일 읽음
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # 4. 이미지 파일 링크 변경해주기
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                filename = src.split('/')[-1]
                if filename in image_files:
                    img['src'] = image_files[filename]

        # 5. 기존 style 삭제
        for style in soup.find_all('style'):
            style.decompose()

        # 6. font 넣기
        head = soup.find('head')
        font_link = soup.new_tag('link', rel='stylesheet', href=PRETENDARD_LINK)
        head.append(font_link)

        # 7. CSS 파일 link로 추가
        new_style_link = soup.new_tag('link', rel='stylesheet', href=CUSTOM_CSS_LINK)
        head.append(new_style_link)

        # 8. HTML 파일 저장 
        with open(temp_html_local_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        # 9. getOcrPdf
        convert_to_ocr_pdf(temp_html_local_path, temp_pdf_local_path)

        # 10. uploadPdf to S3
        upload_pdf(temp_pdf_local_path, S3_BUCKET, output_key)

        # 11. os 파일 정리
        os.remove(temp_zip_local_path)
        os.remove(temp_pdf_local_path)

        return {
            'statusCode': 200,
            'body': {
                'message': 'PDF 변환 완료',
                'requestId': request_uuid,
            }
        }
    
    except Exception as e:
        print(f'handlerError:{e}')
        return {
            'statusCode': 500,
            'body': {
                'message': f'Error: {str(e)}',
                'uuid': request_uuid if 'request_id' in locals() else None
            }
        }
    



# 테스트용
# lambda_handler({'requestId': 'abcd-1234-test-1234'})

lambda_handler()