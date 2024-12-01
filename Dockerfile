FROM python:3.9 AS core

WORKDIR /root

RUN pip3 install ipykernel \
pymongo \
streamlit \
pandas \
streamlit_folium \
plotly \
folium \
pytz

FROM core AS dev

FROM core AS prod

COPY main.py main.py
COPY notebook.ipynb notebook.ipynb

# If not automatically do port forwarding in vscode 80 -> 8501
#CMD ["streamlit", "run", "main.py", "--server.port", "80", "--server.enableXsrfProtection", "false", "--browser.gatherUsageStats", "false"]

ARG VERSION
ENV VERSION=${VERSION}