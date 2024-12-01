FROM python:3.12-slim AS core

WORKDIR /root

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM core AS dev

FROM core AS prod

COPY main.py main.py
COPY notebook.ipynb notebook.ipynb

# If not automatically do port forwarding in vscode 80 -> 8501
#CMD ["streamlit", "run", "main.py", "--server.port", "80", "--server.enableXsrfProtection", "false", "--browser.gatherUsageStats", "false"]

ARG VERSION
ENV VERSION=${VERSION}