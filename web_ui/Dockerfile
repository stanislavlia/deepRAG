FROM python:3.10

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY ./client.py /app/client.py
COPY ./search_ui.py /app/search_ui.py



RUN mkdir tmp



CMD ["streamlit", "run", "--server.port", "8051", "search_ui.py" ]