FROM python:3.12

WORKDIR /flask_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# CMD waitress-serve --call app:app_factory.get_app
