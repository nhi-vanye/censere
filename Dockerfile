FROM python:alpine

RUN mkdir -p /BUILD/censere

ADD requirements.txt  /BUILD/censere/

RUN cd /BUILD/censere \
    && ls -l \
    && apk add --no-cache --virtual .gcc.deps \
        build-base \
        gcc \
        libffi-dev \
        make \
        musl-dev \
    && pip3 install \
        --requirement requirements.txt \
    && apk del .gcc.deps

ADD setup.py  /BUILD/censere/
ADD censere  /BUILD/censere/censere/

RUN cd /BUILD/censere \
    && python3 setup.py bdist_wheel \
    && pip3 install dist/*whl \
    && pip3 list --format=freeze > /root/censere.pip \
    && rm -rf /BUILD/censere


ENTRYPOINT ["python3", "-m", "censere.generator"]
