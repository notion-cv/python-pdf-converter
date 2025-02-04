# 첫 번째 스테이지: 빌드 환경
# pango v1.56.1 을 사용하게끔 만들어야함
FROM public.ecr.aws/lambda/python:3.9 as builder

# 개발 도구 및 시스템 라이브러리 설치
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y \
    cairo \
    cairo-devel \
    harfbuzz \
    harfbuzz-devel \
    gobject-introspection \
    gobject-introspection-devel \
    fribidi \
    fribidi-devel \
    libffi \
    libffi-devel

# Pango 1.56.1 빌드 및 설치
WORKDIR /tmp
RUN pip install meson ninja && \
    curl -LO https://download.gnome.org/sources/pango/1.56/pango-1.56.1.tar.xz && \
    tar xf pango-1.56.1.tar.xz && \
    cd pango-1.56.1 && \
    mkdir build && \
    cd build && \
    meson setup --prefix=/usr .. && \
    ninja && \
    ninja install


# Python 패키지 설치
WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt .
RUN pip install -r requirements.txt --target .

# 런타임 스테이지
FROM public.ecr.aws/lambda/python:3.9

# 런타임에 필요한 시스템 라이브러리 설치
RUN yum update -y && \
    yum install -y \
    poppler-utils \
    tesseract \
    tesseract-langpack-kor \
    ghostscript \
    cairo \
    harfbuzz \
    gobject-introspection \
    fribidi \
    libffi

# Pango 관련 파일들 복사
COPY --from=builder /usr/lib64/libpango* /usr/lib64/
COPY --from=builder /usr/lib64/pango /usr/lib64/pango/
COPY --from=builder /usr/lib/pango /usr/lib/pango/
COPY --from=builder /usr/share/pango /usr/share/pango/
COPY --from=builder /etc/pango /etc/pango/

# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# 빌드 스테이지에서 설치된 Python 패키지 복사
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# 애플리케이션 코드 복사
COPY function/ ./function/
COPY main.py .

# Python 패키지 설치
RUN pip install -r requirements.txt

# 환경변수 설정 (빌드할 때 넣어줘야 함)
ARG S3_BUCKET
ARG CSS_PATH
ENV S3_BUCKET=${S3_BUCKET} \
    CSS_PATH=${CSS_PATH}

RUN pkg-config --modversion pango

# Lambda 핸들러 설정
CMD ["main.lambda_handler"]
