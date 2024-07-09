FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY solution.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./solution.py"]
