# 기본 python 이미지를 지정
# Python 3.12의 slim(경량화) 버전을 베이스 이미지로 사용하여 컨테이너의 크기를 줄임
FROM python:3.12-slim

# 작업 디렉토리 생성
# 컨테이너 내부에서 /app 디렉토리를 작업 디렉토리로 설정
WORKDIR /app

# 필수 패키지 설치
# apt-get을 통해 기본적인 패키지와 PostgreSQL과 관련된 개발 패키지(libpq-dev)를 설치
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    wget \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    pkg-config \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*
# pyenv 설치를 위한 curl
# 빌드 도구 (make, gcc 등)
# SSL 라이브러리 (https 통신 등)
# bzip2 압축 라이브러리
# readline 라이브러리 (터미널 입력 지원)
# PostgreSQL과 Python 연동을 위한 라이브러리
# PostgreSQL과 Python 연동을 위한 라이브러리
# apt 캐시 파일 삭제로 이미지 크기 줄임

# pyenv 설치 및 환경 설정
# pyenv 설치 스크립트를 curl로 실행하고 환경 변수를 설정해 pyenv가 정상 작동하도록 함
RUN curl https://pyenv.run | bash
# pyenv 설치 경로 지정
ENV PYENV_ROOT="/root/.pyenv"
# pyenv가 PATH에 포함되도록 설정
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

# pyenv-virtualenv 설치 확인 및 초기화
# pyenv로 Python 3.12.4 설치 후 가상환경(django_collabo)을 생성
RUN /bin/bash -c "source ~/.bashrc && pyenv install 3.12.4"
RUN /bin/bash -c "source ~/.bashrc && pyenv virtualenv 3.12.4 django_collabo"

# pyenv 환경변수와 초기화 스크립트를 bashrc에 추가해 pyenv를 사용할 수 있도록 설정
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
RUN echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
RUN echo 'pyenv activate django_collabo' >> ~/.bashrc  # 기본적으로 django_collabo 가상환경이 활성화되도록 설정

# poetry 설치
# Poetry 패키지 매니저를 설치해 Python 프로젝트의 의존성 관리를 담당하도록 함
RUN curl -sSL https://install.python-poetry.org | python3 -
# Poetry가 PATH에 포함되도록 설정
ENV PATH="/root/.local/bin:$PATH"

# 의존성 설치
# pyproject.toml 및 poetry.lock 파일을 복사하여 프로젝트의 Python 의존성을 설치
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN /bin/bash -c "source ~/.bashrc && pyenv activate django_collabo && poetry install --no-root"

# 프로젝트 소스 코드 복사
# 로컬 프로젝트 디렉토리를 컨테이너의 /app 디렉토리로 복사하여 Django 소스 코드를 포함시킴
COPY . /app

# ENTRYPOINT 설정
# 컨테이너 시작 시 실행할 entrypoint.sh 스크립트를 /app에 복사하고 실행 권한을 부여
RUN chmod +x /app/scripts/entrypoint.sh
# entrypoint.sh를 ENTRYPOINT로 설정해 컨테이너 시작 시 실행
ENTRYPOINT ["/bin/bash", "/app/scripts/entrypoint.sh"]

# Gunicorn이 8000 포트에서 수신하도록 EXPOSE
# Django 애플리케이션이 8000 포트에서 수신할 수 있도록 포트를 노출
EXPOSE 8000
