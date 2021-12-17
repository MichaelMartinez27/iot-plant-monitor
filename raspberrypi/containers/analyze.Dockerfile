FROM python:3.9-bullseye

RUN pip install --no-warn-script-location --upgrade --user \
        pip \
        paho-mqtt \

RUN pip install --trusted-host --upgrade --user \
        scikit-learn

CMD ["python","/code/data_analysis.py"]