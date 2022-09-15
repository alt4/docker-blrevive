# BLRevive Docker Server

A Docker implementation of the Blacklight: Retribution Revive server.

**NOTE**: As of yet, the Wine setup is pretty much everything-and-the-kitchen-sink. Image weight will be made *much* lighter later down the line.

## Quickstart

```bash
docker build -t docker-blrevive .
docker run -v /srv/blacklightre/:/mnt/blacklightre:ro -p 7777:7777/udp docker-blrevive
```

## Usage

The game's files need to be mounted to `/mnt/blacklightre/`.

### Downloading the game

Downloading Blacklight can be done entirely on Docker using DepotDownloader.

The only pre-requisite is a Steam account that can download BLR:

```bash
STEAM_USERNAME=YOU!
docker run -it -v /srv/blacklightre/gamefiles:/srv/blacklightre/gamefiles mcr.microsoft.com/dotnet/sdk:6.0 bash -c "apt-get update \
  && apt-get install -y unzip \
  && curl -L -O https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.4.7/depotdownloader-2.4.7.zip \
  && unzip depotdownloader-2.4.7.zip \
  && dotnet DepotDownloader.dll -app 209870 -username $STEAM_USERNAME \
  && mv depots/209871/2520205/ /srv/blacklightre/"
```

Applying BLRE's patch is going to be more finicky: current launcher releases do not support CLI patching properly.

Your best bet is patching the game manually elsewhere and copying `FoxGame-win32-Shipping-Patched-Server.exe` to `/srv/blacklightre/Binaries/Win32` (without the proxy, see #1).

### Building the image

Clone the repository and run

```bash
docker build -t docker-blrevive .
```

### Starting a server

Run:

```bash
docker run -v /srv/blacklightre/:/mnt/blacklightre:ro -p 7777:7777/udp docker-blrevive
```
