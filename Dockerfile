# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
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

# pyenv 설치
RUN curl https://pyenv.run | bash

# pyenv 환경 변수 설정
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

# pyenv 및 pyenv-virtualenv 초기화
RUN echo 'export PYENV_ROOT="/root/.pyenv"' >> ~/.bashrc
RUN echo 'export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# bashrc를 소싱하도록 프로파일 설정 추가
RUN echo "source ~/.bashrc" >> ~/.profile

# Python 설치 및 가상 환경 생성
RUN /bin/bash -c "source ~/.bashrc && pyenv install 3.12.4 && pyenv virtualenv 3.12.4 django-collabo"

# Poetry 설치 및 PATH 설정
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Poetry 가상 환경 비활성화 (pyenv 가상 환경을 사용)
RUN poetry config virtualenvs.create false

# 프로젝트 종속성 파일 복사 및 설치
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN /bin/bash -c "source ~/.bashrc && pyenv activate django-collabo && poetry install --no-root"

# 프로젝트 소스 복사
COPY . /app

# ENTRYPOINT 스크립트 복사 및 실행 권한 부여
RUN chmod +x /app/scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "-c", "source ~/.bashrc && /app/scripts/entrypoint.sh"]

# 포트 노출
EXPOSE 8000