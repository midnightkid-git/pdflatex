    
FROM python:3.9.0
FROM alpine:3.4
CMD ["/bin/sh"]

RUN groupadd -r pdflatex
RUN useradd --system -g pdflatex pdflatex
RUN apk add --no-cache --repository /packages     texlive     texmf-dist-latexextra     py3-aiohttp
RUN python3 -m pip install pip --upgrade
RUN pip install aiohttp
RUN apt-get install -y latexmk
WORKDIR /usr/app/src
COPY pdflatex.py ./
USER pdflatex
EXPOSE 8080
CMD [ "python3", "./pdflatex.py"]
