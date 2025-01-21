FROM python
WORKDIR /app
RUN pip install "fastapi[standard]"
COPY modelranking.py ./
CMD [ "fastapi", "run", "modelranking.py", "--port", "80"]