FROM alpine:3.15.4 AS base

FROM base AS build
RUN echo "x86" > /etc/apk/arch && apk update && apk add alpine-sdk sudo
RUN adduser -Dh /builder builder && \
    adduser builder abuild && \
    echo 'builder ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/builder

USER builder
RUN mkdir -p /builder/src/main /builder/packages/main && \
    abuild-keygen -ain

FROM build AS build-wine
COPY --chown=builder:builder ./src/wine/ /builder/src/main/wine/
RUN ulimit -n 1024; cd /builder/src/main/wine && abuild -r

FROM base

RUN apk add --no-cache gnutls tzdata ca-certificates sudo xvfb python3 py3-pip

# Wine build
# Kaniko doesn't support RUN --mount yet... https://github.com/GoogleContainerTools/kaniko/issues/1568
# RUN --mount=from=build-wine,source=/builder/packages/main/x86,target=/builder/wine \
#     echo "x86" > /etc/apk/arch && apk add --no-cache --allow-untrusted /builder/wine/blrevive-server-wine-[0-9]*-r*.apk
COPY --from=build-wine /builder/packages/main/x86 /builder/wine
RUN echo "x86" > /etc/apk/arch && apk add --no-cache --allow-untrusted /builder/wine/blrevive-server-wine-[0-9]*-r*.apk && \
    rm -rf /builder/wine

# silence Xvfb xkbcomp warnings by working around the bug (present in libX11 1.7.2) fixed in libX11 1.8 by https://gitlab.freedesktop.org/xorg/lib/libx11/-/merge_requests/79
RUN echo 'partial xkb_symbols "evdev" {};' > /usr/share/X11/xkb/symbols/inet

# M.A.R.S preparation
WORKDIR /srv/mars
COPY ./src/mars/requirements-gunicorn.txt /srv/mars/requirements-gunicorn.txt
COPY ./src/start.sh /srv/mars/start.sh
RUN pip install -r requirements-gunicorn.txt && \
  chmod +x start.sh
COPY ./src/mars/ /srv/mars

# Finalization
RUN adduser -D blrevive && \
    echo 'blrevive ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/blrevive && \
    mkdir /mnt/blacklightre
USER blrevive

ENV WINEDEBUG=-d3d
ENV WINEPREFIX="/home/blrevive/.wine"
RUN WINEDLLOVERRIDES="mscoree,mshtml=,winemenubuilder.exe" wineboot --init

VOLUME /mnt/blacklightre

ENV PATH="/opt/marsvenv/bin:$PATH"

ENV MARS_API_LISTEN_IP=127.0.0.1
ENV MARS_API_LISTEN_PORT=5000

EXPOSE 7777/udp
EXPOSE 5000/tcp

CMD ["start.sh"]