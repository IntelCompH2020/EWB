
FROM python:3.9

WORKDIR /restapi

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python3", "restAPI.py"]