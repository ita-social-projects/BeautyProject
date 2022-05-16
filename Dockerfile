FROM python:3.9.12-alpine

# Console output in real time and no *.pyc files
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements.txt /requirements.txt

# Install required packages
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev \ 
    linux-headers postgresql-dev postgresql-client
RUN pip install -r /requirements.txt

# Copy project
RUN mkdir ./app
COPY . /app
WORKDIR /app
COPY ./scripts /scripts

# Make files in scripts folder executable
RUN chmod +x /scripts/*

# Folders for media and static
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Add new user
RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
USER user

CMD ["entrypoint.sh"]
