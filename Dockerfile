# https://docs.streamlit.io/deploy/tutorials/docker

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1

# create venv and add to path
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt /app
COPY packages.txt /app

RUN apt-get update \
    && xargs apt install -y < packages.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir -r requirements.txt

COPY . /app

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# run using for example
#     docker run -p 8501:8501 -it <tag>