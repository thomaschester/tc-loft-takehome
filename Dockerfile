FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# "-u": Unbuffered to write logs immediately instead of to temp storage
CMD ["python", "-u", "-m", "src.main"]
