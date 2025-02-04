FROM public.ecr.aws/lambda/python:3.13

# 시스템 라이브러리 설치
RUN yum update -y && \
    yum install -y \
    poppler-utils \
    tesseract \
    tesseract-langpack-kor \
    ghostscript \
    pango \      
    pango-devel \ 
    libffi-devel \
    cairo \       
    cairo-devel \ 
    gcc

# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# 파일 복사
COPY requirements.txt .
COPY function/ ./function/
COPY main.py .

# Python 패키지 설치
RUN pip install -r requirements.txt

# 환경변수 설정 (빌드할 때 넣어줘야 함)
ARG S3_BUCKET
ARG CSS_PATH
ENV S3_BUCKET=${S3_BUCKET} \
    CSS_PATH=${CSS_PATH}

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]