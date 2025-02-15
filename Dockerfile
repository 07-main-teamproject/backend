FROM python:3.13-alpine3.20

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요 파일 복사
COPY requirements.txt .

# 4. 패키지 설치 (gunicorn 포함)
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 파일 복사
COPY . .

# 6. 정적 파일 모으기
RUN python manage.py collectstatic --noinput

# 7. 실행 명령어 설정
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--timeout", "300", "main_project_07.wsgi:application"]

