FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    bandit pip-audit
COPY app/ app/
EXPOSE 8000
CMD ["python", "app/main.py"]
