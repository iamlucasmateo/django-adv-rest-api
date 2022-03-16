FROM python:3.7-alpine

# usual config for Python
ENV PYTHON_UNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# adding Postgresql to our container
# --no-cache: dont add registry data to our image
RUN apk add --update --no-cache postgresql-client jpeg-dev
# dependencies for installing requirements (Postgres) in alpine image
# --virtual tags these dependencies so that we can later delete them 
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt

# deleting dependencies
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# this is for images (typical Django names for folders)
# -p is for creating all directories in the indicated path
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
# this user creation is in order for the app not to have access to the root user
# -D, user is only for running applications
RUN adduser -D user
# giving permissions to user
RUN chown -R user:user /vol/
RUN chown -R 755 /vol/web
# change user, so as not to use root user (limiting access for security)
USER user

