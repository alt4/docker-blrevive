# BLRevive Docker Server

A Docker implementation of the Blacklight: Retribution Revive server.

## Downloading the game's files

Downloading the game's files can be done entirely on Docker using DepotDownloader.

The only pre-requisite is a Steam account that can download BLR:

```bash
STEAM_USERNAME=YOU!
docker run -it -v /srv/blacklightre/gamefiles:/srv/blacklightre/gamefiles mcr.microsoft.com/dotnet/sdk:6.0 bash -c "apt-get update \
  && apt-get install -y unzip \
  && curl -L -O https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.4.7/depotdownloader-2.4.7.zip \
  && unzip depotdownloader-2.4.7.zip \
  && dotnet DepotDownloader.dll -app 209870 -username $STEAM_USERNAME \
  && mv depots/209871/2520205/ /srv/blacklightre/gamefiles/"
```
