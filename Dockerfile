FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . requirements.txt /home
RUN pip3 install --no-cache-dir --upgrade -r /home/requirements.txt

COPY . /home

EXPOSE 8080

WORKDIR home

CMD ["python3", "adv.py"]