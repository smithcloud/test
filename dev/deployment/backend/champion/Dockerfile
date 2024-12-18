FROM python:3.9-alpine
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn","champions:app","--host=0.0.0.0","--reload"]