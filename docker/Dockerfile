FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update && \
    apt-get -y install texlive-full make python3-pygments

COPY fonts/ /root/.fonts/

WORKDIR /app