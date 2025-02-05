FROM public.ecr.aws/lambda/python:3.13

# EPEL 저장소 추가 및 시스템 라이브러리 설치
RUN dnf update -y && \
    dnf install -y \
        dnf-utils && \
    dnf config-manager --set-enabled \
        crb && \
    dnf install -y \
        https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \
    dnf install -y \
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

# 환경변수 설정
ARG S3_BUCKET
ARG CSS_PATH
ENV S3_BUCKET=${S3_BUCKET} \
    CSS_PATH=${CSS_PATH}

# Pango 버전 확인
RUN pkg-config --modversion pango

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]