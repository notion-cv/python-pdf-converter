FROM public.ecr.aws/lambda/python:3.13

# 시스템 라이브러리 설치
RUN dnf update -y && \
    dnf install -y \
    poppler-utils \
    ghostscript \
    pango \
    pango-devel \
    libffi-devel \
    cairo \
    cairo-devel \
    gcc \
    make \
    automake \
    autoconf \
    libtool \
    pkgconfig \
    libjpeg-devel \
    libpng-devel \
    libtiff-devel \
    zlib-devel \
    gcc-c++ \
    wget \
    git

# 환경 변수 설정
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Leptonica 설치
RUN cd /tmp && \
    wget https://github.com/DanBloomberg/leptonica/releases/download/1.83.1/leptonica-1.83.1.tar.gz && \
    tar -xzvf leptonica-1.83.1.tar.gz && \
    cd leptonica-1.83.1 && \
    ./configure && \
    make && \
    make install


# Tesseract 설치
RUN cd /tmp && \
    wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.3.3.tar.gz && \
    tar -xzvf 5.3.3.tar.gz && \
    cd tesseract-5.3.3 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install

# 한국어 데이터 설치
RUN cd /tmp && \
    wget https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata && \
    mkdir -p /usr/local/share/tessdata && \
    mv kor.traineddata /usr/local/share/tessdata/

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
    CSS_PATH=${CSS_PATH} \
    LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH \
    TESSDATA_PREFIX=/usr/local/share/tessdata

# Pango 버전 확인
RUN pkg-config --modversion pango

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]