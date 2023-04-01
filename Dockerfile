FROM golang:1.20.2-alpine3.17 as builder

WORKDIR /go/src/northamp/docker-blrevive-entrypoint
COPY /src/entrypoint/* .
RUN set -x && \
    go get -d -v . && \
    CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o docker-blrevive-entrypoint .

FROM alpine:3.17.3

# Wine and user setup - done first for caching purposes
COPY ./pkg /builder/wine
RUN echo "x86" > /etc/apk/arch && apk add --no-cache --allow-untrusted /builder/wine/blrevive-server-wine-[0-9]*-r*.apk && \
    rm -rf /builder/wine

RUN adduser -Dh /blrevive blrevive

USER blrevive

ENV WINEDEBUG=-d3d
ENV WINEPREFIX="/blrevive/.wine"
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

USER root

RUN apk add --no-cache gnutls tzdata ca-certificates xvfb

# silence Xvfb xkbcomp warnings by working around the bug (present in libX11 1.7.2) fixed in libX11 1.8 by https://gitlab.freedesktop.org/xorg/lib/libx11/-/merge_requests/79
RUN echo 'partial xkb_symbols "evdev" {};' > /usr/share/X11/xkb/symbols/inet

COPY --from=builder /go/src/northamp/docker-blrevive-entrypoint/docker-blrevive-entrypoint /usr/local/bin/docker-blrevive

USER blrevive

VOLUME /mnt/blacklightre

EXPOSE 7777/udp

CMD ["docker-blrevive"]