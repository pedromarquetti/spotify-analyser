FROM python:3.10.12

# copying project
COPY . .

# installing deps
RUN pip3 install -r requirements.txt

CMD ["python3", "./main.py"]


