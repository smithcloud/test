FROM python:3.9
COPY admin.py .
RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install faker
CMD ["streamlit","run","admin.py"]