# syntax=docker/dockerfile:latest

FROM python:alpine as base

RUN mkdir -p /censere /BUILD/censere

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --upgrade pip

WORKDIR "/BUILD/censere"

#####################################################
FROM base as builder

# Keep this early to maximize the docker layer cache re-use
RUN apk add --no-cache \
        build-base \
        freetype-dev \
        gcc \
        libffi-dev \
        make \
        musl-dev \
        openblas \
        openblas-dev

RUN pip3 install --upgrade build

# pre-install the time-consuming bits (pandas etc)
# so we can make use of the docker layer cache...
RUN pip install --user --no-warn-script-location \
    Cython \
    dash \
    dash-core-components \
    dash-html-components \
    dash-table \
    numpy \
    pandas \
    peewee

ADD setup.py  pyproject.toml *.md /BUILD/censere/
ADD censere  /BUILD/censere/censere/

RUN pip install --user --no-warn-script-location .

RUN ls -al $HOME/.local/

#####################################################
FROM base as production

RUN apk add --no-cache \
        libstdc++ \
        openblas

# copy the wheel from the build stage
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

RUN pip list --format=freeze > /root/requirements.txt

ENTRYPOINT ["/root/.local/bin/mars-censere"]
