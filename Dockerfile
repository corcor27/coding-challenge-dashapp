FROM continuumio/miniconda3

COPY requirements.txt /tmp/
COPY ./app /app
WORKDIR "/app"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN conda install -c conda-forge --file /tmp/requirements.txt
RUN pip install dash-auth google-auth google-api-python-client
ENTRYPOINT [ "python3" ]
CMD [ "plotly_dashboard.py" ]
