FROM debian:bullseye

RUN apt-get update && apt-get install -y wget gnupg

# Adapted from scottyhardy/docker-wine, a MIT-licensed project
RUN wget -nv -O- https://dl.winehq.org/wine-builds/winehq.key | APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1 apt-key add - \
    && echo "deb https://dl.winehq.org/wine-builds/debian/ $(grep VERSION_CODENAME= /etc/os-release | cut -d= -f2) main" >> /etc/apt/sources.list \
    && dpkg --add-architecture i386 \
    && apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y --install-recommends winehq-stable \
    && rm -rf /var/lib/apt/lists/*

# Taken from DomiStyle/docker-eldewrito, a (very similar) MIT-licensed project
RUN WINEDLLOVERRIDES="mscoree,mshtml=" wineboot -u

VOLUME /mnt/blacklightre

EXPOSE 7777/udp

WORKDIR /mnt/blacklightre/gamefiles/Binaries/Win32

CMD wine FoxGame-win32-Shipping-Patched.exe server HeloDeck?Game=FoxGame.FoxGameMP_TDM?NumBots=10?port=7777