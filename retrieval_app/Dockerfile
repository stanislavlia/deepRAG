FROM tiangolo/uvicorn-gunicorn:python3.10

COPY ./requirements.txt /app/requirements.txt

COPY ./api_schemas.py /app/api_schemas.py
COPY ./app.py /app/app.py
COPY ./pdf_utils.py /app/pdf_utils.py
COPY ./vecdb_utils.py /app/vecdb_utils.py
COPY ./text_cleaning.py /app/text_cleaning.py

WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]
