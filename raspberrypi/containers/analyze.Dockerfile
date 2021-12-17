FROM python:3.9-bullseye

RUN pip install --no-warn-script-location --upgrade --user \
        pip \
        paho-mqtt \
        flask \
        plotly \
        pycaret \
        scipy

CMD ["python","/code/data_analysis.py"]