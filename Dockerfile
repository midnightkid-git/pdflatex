    
FROM python:3.9.0

CMD ["/bin/sh"]

RUN apt-get update -y
RUN python3 -m pip install pip --upgrade
RUN pip install aiohttp
RUN apt-get install -y latexmk
RUN apt-get -y install texlive-latex-recommended texlive-pictures texlive-latex-extra

WORKDIR /usr/app/src
COPY pdflatex.py ./

EXPOSE 8080
CMD [ "python3", "./pdflatex.py"]
