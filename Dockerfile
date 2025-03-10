FROM python:3.13

RUN useradd -ms /bin/bash sockie 
USER sockie
WORKDIR /home/sockie/sockbot
COPY . .
RUN pip install -r requirements.txt

# unbuffered!
CMD ["python3", "-u", "bot.py"]
