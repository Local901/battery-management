# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --break-system-packages

# Copy root filesystem
COPY rootfs /
