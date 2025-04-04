FROM python:3.10.14 as backend



WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt 

ENTRYPOINT pip3 install -r requirements.txt && python3 -Xfrozen_modules=off .




FROM python:3.10 as rvc-api

WORKDIR /app


COPY rvc_models/ ./rvc_models

RUN pip3 install rvc-python && \
    pip3 install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install tensorboardX

ENTRYPOINT [ "python3","-m","rvc_python","api","-l" ]





