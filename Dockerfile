FROM 10.32.42.225:5000/python:3.7-buster
USER root
WORKDIR /usr/src/app
COPY requirements.txt ./

# set timezone 
ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN export http_proxy="http://proxy.charite.de:8080/"
RUN export https_proxy="http://proxy.charite.de:8080/"


RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["./gunicorn_starter.sh"]
# CMD ["python","app.py"]
