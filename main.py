import os
import zipfile
from bs4 import BeautifulSoup
from typing import Dict, Any
from dotenv import load_dotenv
import glob

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
        request_id_key = 'requestId'
        # UUID 존재 및 유효성 체크
        if request_id_key not in event or not event[request_id_key] or not isinstance(event[request_id_key], str):
            return {
                'statusCode': 400,
                'bodypdf-converter': {
                    'message': '요청이 유효하지 않습니다.'
                }
            }
        
        request_uuid = event.get(request_id_key).strip() # 앞뒤 공백 제거
        input_key = f"temp/{request_uuid}/{request_uuid}.zip"
        output_key = f"temp/{request_uuid}/{request_uuid}.result.pdf"

        print(f'requestID 존재함 / requestId: {request_uuid}')

        # 임시 로컬 파일 경로 설정
        temp_zip_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.zip")
        temp_extracted_files_path = os.path.join(LOCAL_TEMP_DIR, 'extracted/')
        temp_html_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.html")
        temp_pdf_local_path = os.path.join(LOCAL_TEMP_DIR, f"{request_uuid}.pdf")
        
        # zip 파일 다운로드
        download_zip(S3_BUCKET, input_key, temp_zip_local_path)
        print(f'zip 파일 다운로드 완료  / temp_zip_local_path: {temp_zip_local_path}')

        # 1. zip 파일 압축 해제
        # issue) lambda에서는 zip 파일 받으면 뒤에 문자를 더 붙이기도 함
        actual_files = glob.glob(f"{temp_zip_local_path}*")
        if actual_files:
            actual_file_path = actual_files[0]
            print(f"Actual file path: {actual_file_path}")
            
            with zipfile.ZipFile(actual_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extracted_files_path)

        print('zip 파일 압축 성공!')

        # 2. HTML 파일과 에셋 디렉토리 찾기
        html_file, image_files = extract_files(temp_extracted_files_path)

        if not html_file:
            return {
                'statusCode': 400,
                'body': 'HTML file not found in ZIP'
            }
        
        print('HTML, image 찾기 성공')

        # 3. HTML 파일 읽음
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        print('HTML 파일 읽기 완료')
        
        # 4. 이미지 파일 링크 변경해주기
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                filename = src.split('/')[-1]
                if filename in image_files:
                    img['src'] = image_files[filename]

        print('이미지 파일 링크 변경 성공!')

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

        print('스타일 변경 성공')

        # 8. HTML 파일 저장 
        with open(temp_html_local_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print('HTML 저장')

        # 9. getOcrPdf
        convert_to_ocr_pdf(temp_html_local_path, temp_pdf_local_path)

        print('PDF 변환 완료')

        # 10. uploadPdf to S3
        upload_pdf(temp_pdf_local_path, S3_BUCKET, output_key)

        print('s3에 PDF 저장')

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
                'requestId': request_uuid
            }
        }
    



# 테스트용
# lambda_handler({'requestId': 'abcd-1234-test-1234'})
