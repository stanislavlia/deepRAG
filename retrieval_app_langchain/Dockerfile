FROM tiangolo/uvicorn-gunicorn:python3.10

COPY ./requirements.txt /app/requirements.txt
COPY ./preload_model.py /app/preload_model.py

WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#download embedding model 
RUN python3 preload_model.py

COPY ./app.py /app/app.py
COPY ./retrieval.py /app/retrieval.py

RUN pip install pypdf

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]




