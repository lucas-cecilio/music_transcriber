FROM python:3.10-bookworm

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-sdk -y

RUN apt update && apt install libfluidsynth3 build-essential libasound2-dev libjack-dev gdal-bin libgdal-dev libcairo2-dev pkg-config python3-dev ffmpeg fluidsynth musescore fluid-soundfont-gm -y

RUN apt-get install -y \
qtbase5-dev \
libxcb-xinerama0 \
libxcb1-dev \
libxkbcommon-x11-0

ENV QT_QPA_PLATFORM=offscreen

COPY . /music_transcriber

WORKDIR /music_transcriber

RUN make install_all

CMD uvicorn api:app --reload --loop asyncio --host 0.0.0.0
