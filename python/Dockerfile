FROM python:3.12.0a7-alpine3.17

RUN adduser --disabled-password --gecos "" pgen
USER pgen
WORKDIR /home/pgen/
ENV PATH="/home/pgen/.local/bin:${PATH}"

RUN pip install --upgrade pip

COPY --chown=pgen:pgen requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

COPY --chown=pgen:pgen pgen .

CMD ["python", "main.py"]

