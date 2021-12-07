FROM python:3.9

RUN pip install --upgrade --user pip
RUN pip install --upgrade --user paho-mqtt
RUN pip install --upgrade --user flask
RUN pip install --upgrade --user plotly
RUN pip install --upgrade --user pandas

CMD ["python","/code/data_visual.py"]
