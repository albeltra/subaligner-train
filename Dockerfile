FROM ubuntu

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN apt update

RUN apt install -y python3 python3-pip git wget ffmpeg libsndfile-dev

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest-Linux-x86_64.sh &&\
    chmod +x Miniconda3-latest-Linux-x86_64.sh &&\
    bash Miniconda3-latest-Linux-x86_64.sh -b

RUN conda install -c conda-forge gxx

COPY ./plex-audio-subtitle-switcher /plex-audio-subtitle-switcher

RUN cd /plex-audio-subtitle-switcher && python3 setup.py

COPY ./subaligner /subaligner

RUN cd /subaligner && python3 -m pip install .
