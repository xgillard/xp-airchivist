FROM python:3.10-alpine
WORKDIR /app
RUN pip install "fastapi[standard]"
COPY modelranking.py ./
CMD [ "fastapi", "run", "modelranking.py", "--port", "80"]