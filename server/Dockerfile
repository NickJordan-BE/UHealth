FROM python:3.11-slim
WORKDIR /server-app
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
CMD ["flask", "--app", "server", "run"]