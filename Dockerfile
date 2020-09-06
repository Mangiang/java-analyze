FROM python:3.6-alpine

RUN apk add --no-cache git

RUN addgroup -S pythonGroup && adduser -S pythonUser -G pythonGroup

USER pythonUser

WORKDIR /home/pythonUser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY src ./src

# Uncomment to get the base image name and distribution
# RUN cat /etc/*-release

ENTRYPOINT python main.py -d . -r https://github.com/Mangiang/test-spring-boot.git