FROM python:3.9

RUN pip install --upgrade --user pip paho-mqtt flask plotly pandas

CMD ["python","/code/data_visual.py"]