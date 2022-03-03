FROM python:3.7-alpine

# usual config for Python
ENV PYTHON_UNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# this user creation is in order for the app not to have access to the root user
# -D, user is only for running applications
RUN adduser -D user
USER user

