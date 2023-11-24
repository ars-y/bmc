FROM python:3.10

RUN mkdir /bmc_app

WORKDIR /bmc_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x scripts/*.sh