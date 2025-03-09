FROM python:3.12

WORKDIR /sockbot
COPY . .
RUN pip install -r requirements.txt

CMD ["python3", "-u", "bot.py"]