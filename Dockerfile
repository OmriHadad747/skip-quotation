FROM tiangolo/uwsgi-nginx:python3.10


ENV APP_DIR /skip-quotation


# update and install packages
RUN apt-get update
RUN apt install -y build-essential \
                    git \
                    openssh-client \ 
                    ca-certificates \
                    netcat \
                    iputils-ping


# update to the latest pip
RUN pip3 install --upgrade pip


# Our application code will exist in the /app directory,
# so set the current working directory to that
WORKDIR ${APP_DIR}


ADD skip-quotation/app ./app
ADD skip-quotation/resources ./resources
ADD skip-quotation/requirements ./
ADD skip-quotation/run.py ./


RUN  pip3 install -r requirements --no-cache-dir


CMD python run.py