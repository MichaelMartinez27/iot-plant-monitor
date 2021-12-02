FROM python:3.9

RUN pip install --upgrade --user pip
RUN pip install --upgrade --user paho-mqtt

CMD ["python","/code/data_storage.py"]