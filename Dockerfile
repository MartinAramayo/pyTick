FROM python:3.11-alpine

WORKDIR /usr/src/app

RUN apk update
RUN apk add py3-numpy py3-pandas
ENV PYTHONPATH=/usr/lib/python3.11/site-packages

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "pyTick_cli.py"]
CMD ["--help"]
