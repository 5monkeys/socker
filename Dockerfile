FROM python:3.4-onbuild

EXPOSE 8765

RUN apt-get update && apt-get -y install wamerican
RUN python setup.py develop

ENTRYPOINT ["socker"]
