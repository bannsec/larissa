FROM ubuntu:17.04

RUN adduser larissa

RUN mkdir /larissa

WORKDIR /larissa

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libboost-all-dev cmake python2.7-dev python-virtualenv g++ git virtualenvwrapper gcc-multilib

COPY . .

RUN chown -R larissa:larissa .

USER larissa

RUN mkdir ~/.virtualenvs
RUN virtualenv --python=$(which python2) ~/.virtualenvs/larissa

RUN bash -c "echo 'source ~/.virtualenvs/larissa/bin/activate' >> /home/larissa/.bashrc"

RUN bash -c "source ~/.virtualenvs/larissa/bin/activate && pip install .[dev]"

# Drop user into home/larissa
WORKDIR /home/larissa

CMD bash
