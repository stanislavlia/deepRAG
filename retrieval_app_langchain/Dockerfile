FROM tiangolo/uvicorn-gunicorn:python3.10

COPY ./requirements.txt /app/requirements.txt
COPY ./preload_model.py /app/preload_model.py

WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#download embedding model 
RUN python3 preload_model.py


COPY ./app.py /app/app.py
COPY ./retrieval.py /app/retrieval.py
COPY ./localstack_s3.py /app/localstack_s3.py
COPY ./corrective_rag.py /app/corrective_rag.py
COPY ./.env /app/.env

RUN pip install pypdf
RUN pip install openai


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]




