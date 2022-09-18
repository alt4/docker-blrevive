# syntax=docker/dockerfile:1.3

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
RUN apk add --no-cache gnutls tzdata ca-certificates sudo xvfb
# Kaniko doesn't support RUN --mount yet... https://github.com/GoogleContainerTools/kaniko/issues/1568
# RUN --mount=from=build-wine,source=/builder/packages/main/x86,target=/builder/wine \
#     echo "x86" > /etc/apk/arch && apk add --no-cache --allow-untrusted /builder/wine/blrevive-server-wine-[0-9]*-r*.apk
COPY --from=build-wine /builder/packages/main/x86 /builder/wine
RUN echo "x86" > /etc/apk/arch && apk add --no-cache --allow-untrusted /builder/wine/blrevive-server-wine-[0-9]*-r*.apk && \
    rm -rf /builder/wine

# silence Xvfb xkbcomp warnings by working around the bug (present in libX11 1.7.2) fixed in libX11 1.8 by https://gitlab.freedesktop.org/xorg/lib/libx11/-/merge_requests/79
RUN echo 'partial xkb_symbols "evdev" {};' > /usr/share/X11/xkb/symbols/inet

RUN adduser -D blrevive && \
    echo 'blrevive ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/blrevive && \
    mkdir /mnt/blacklightre
USER blrevive

ENV WINEPREFIX="/home/blrevive/.wine"
RUN WINEDLLOVERRIDES="mscoree,mshtml=,winemenubuilder.exe" wineboot --init && \
    for x in \
        /home/blrevive/.wine/drive_c/"Program Files"/"Common Files"/System/*/* \
        /home/blrevive/.wine/drive_c/windows/* \
        /home/blrevive/.wine/drive_c/windows/system32/* \
        /home/blrevive/.wine/drive_c/windows/system32/drivers/* \
        /home/blrevive/.wine/drive_c/windows/system32/wbem/* \
        /home/blrevive/.wine/drive_c/windows/system32/spool/drivers/x64/*/* \
        /home/blrevive/.wine/drive_c/windows/system32/Speech/common/* \
        /home/blrevive/.wine/drive_c/windows/winsxs/*/* \
    ; do \
        orig="/usr/lib/wine/i386-windows/$(basename "$x")"; \
        if cmp -s "$orig" "$x"; then ln -sf "$orig" "$x"; fi; \
    done && \
    for x in \
        /home/blrevive/.wine/drive_c/windows/globalization/sorting/*.nls \
        /home/blrevive/.wine/drive_c/windows/system32/*.nls \
    ; do \
        orig="/usr/share/wine/nls/$(basename "$x")"; \
        if cmp -s "$orig" "$x"; then ln -sf "$orig" "$x"; fi; \
    done

VOLUME /mnt/blacklightre

EXPOSE 7777/udp

# Temporary
COPY --chown=blrevive:blrevive ./src/gamemanager/start.sh /srv/blacklightre/start.sh

WORKDIR /srv/blacklightre
RUN chmod +x start.sh
ENTRYPOINT ["sh", "start.sh"]
CMD ["wine", "FoxGame-win32-Shipping-Patched-Server.exe server HeloDeck?Game=FoxGame.FoxGameMP_TDM?NumBots=10?port=7777"]