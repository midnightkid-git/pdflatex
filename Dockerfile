FROM ubuntu:16.04
FROM python:3.9.0
RUN apt-get update && apt-get install -y \
    software-properties-common \
    vim \
    wget \
    build-essential \
    python3-dev \
    python3-pip \
    curl \
    alien \
    libaio1 \
    libaio-dev \
    libxrender1 \
    libfontconfig1 \
    rpm2cpio \
    cpio \
    unzip \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev

RUN python3 -m pip install pip --upgrade
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN wget -qO- "https://yihui.name/gh/tinytex/tools/install-unx.sh" | sh
RUN mkdir /src
RUN rm -rf /src/TinyTeX
RUN mv /root/.TinyTeX /src/TinyTeX
RUN ln -s /src/TinyTeX/bin/x86_64-linux/pdflatex /usr/local/bin/pdflatex
RUN ln -s /src/TinyTeX/bin/x86_64-linux/tlmgr /usr/local/bin/tlmgr
RUN /src/TinyTeX/bin/x86_64-linux/tlmgr path add \
    && /src/TinyTeX/bin/x86_64-linux/tlmgr install \
    amsfonts \
    amsmath \
    auxhook \
    catchfile \
    fancyhdr \
    fancyvrb \
    float \
    fourier \
    fouriernc \
    fvextra \
    geometry \
    gettitlestring \
    hyperref \
    hyphenat \
    ifplatform \
    kvoptions \
    lastpage \
    lineno \
    minted \
    ms \
    ncntrsbk \
    parskip \
    psnfss \
    rerunfilecheck \
    textpos \
    url \
    xcolor \
    xstring \
    cm-super

WORKDIR /usr/app/src
COPY pdflatex.py ./

EXPOSE 8080
CMD [ "python3", "./pdflatex.py"]