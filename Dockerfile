FROM python:3.12-slim AS core

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8502

CMD ["streamlit", "run", "Liver_Tracker.py", "--server.address=0.0.0.0", "--server.port=8502"]