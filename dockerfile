# 애플리케이션 dockerfile (lambda에 올리는 용)


ARG AWS_ACCOUNT_ID
ARG AWS_REGION

FROM ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/notion-cv/converter-base:latest

# 환경변수 설정
ARG S3_BUCKET
ARG CSS_PATH
ENV S3_BUCKET=${S3_BUCKET} \
    CSS_PATH=${CSS_PATH} \
    AWS_REGION=${AWS_REGION} \
    LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH \
    TESSDATA_PREFIX=/usr/local/share/tessdata


# 작업 디렉토리 설정
WORKDIR ${LAMBDA_TASK_ROOT}

# 파일 복사
COPY requirements.txt .
COPY function/ ./function/
COPY main.py .

# Python 패키지 설치
RUN pip install -r requirements.txt




# Lambda 핸들러 설정
CMD ["main.lambda_handler"]