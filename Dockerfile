FROM python:3.7-alpine
LABEL Franco Del Castillo

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# Add jpeg-dev dependency to our permanent dependencies
RUN apk add --update --no-cache postgresql-client jpeg-dev
# temporary dependencies just for installing the pip packages
RUN apk add --update --no-cache --virtual .tmp-build-deps linux-headers \
        gcc libc-dev postgresql-dev musl-dev zlib-dev
RUN pip install -r /requirements.txt
# we dont remove (del) after install the requirements
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# create two new directories
# map vol and share it with the web server container
# -p to make all the subdirectories that we need
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Running as root user
RUN adduser -D user
# before swith to user give permission to view or access these files
# ownership all the directories in the vol to our custom user
# -R means recursive, set permissions in any subdirectories in vol
RUN chown -R user:user /vol/
# adding permissions
# 755 = user can do everything with the directory
# the rest can read and execute from the directory
RUN chmod -R 755 /vol/web
USER user