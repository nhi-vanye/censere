FROM python:alpine as base

RUN mkdir -p /censere /BUILD/censere

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --upgrade pip

WORKDIR "/BUILD/censere"

#####################################################
FROM base as builder

#ADD requirements.txt  /BUILD/censere/

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

#RUN cd /BUILD/censere \
#    && pip3 install Cython
#RUN cd /BUILD/censere \
#    && pip3 install numpy
#RUN cd /BUILD/censere \
#    && pip3 install pandas
#    && pip3 install \
#        --requirement requirements.txt \
#RUN cd /BUILD/censere \
#    && apk del .gcc.deps

ADD setup.py  /BUILD/censere/
ADD pyproject.toml  /BUILD/censere/
ADD censere  /BUILD/censere/censere/


#RUN python3 -m build

RUN pip install --user .

RUN ls -al $HOME/


#    && pip3 install dist/*.whl \
#    && pip3 list --format=freeze > /root/censere.pip \
#    && rm -rf /BUILD/censere

#####################################################
FROM base as production

RUN apk add --no-cache \
        openblas

# copy the wheel from the build stage
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

#ENTRYPOINT ["python3", "-m", "censere.generator"]
ENTRYPOINT ["/root/.local/bin/mars-censere"]
