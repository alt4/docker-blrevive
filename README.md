# BLRevive Docker Server

A Docker implementation of the [Blacklight: Retribution Revive](https://gitlab.com/blrevive) server.

**NOTE**: Requires a dual-core processor due to a BL:R warning that cannot be acknowledged on headless instances (yet). While it seems promising, performance wasn't thoroughly evaluated yet. Use at your own risks!

## Usage

The game's files need to be mounted to `/mnt/blacklightre/`.

```bash
docker run -v /srv/blacklightre/:/mnt/blacklightre:ro -p 7777:7777/udp registry.gitlab.com/northamp/docker-blrevive:latest
```

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

Your best bet is patching the game manually elsewhere and copying the binaries to `/srv/blacklightre/Binaries/Win32`.

### Different parameters

Server settings can be overriden in this manner (temporary, will probably move to environment variables later):

```bash
docker run -v /srv/blacklightre/:/mnt/blacklightre:ro -p 7777:7777/udp registry.gitlab.com/northamp/docker-blrevive:latest wine FoxGame-win32-Shipping-Patched.exe server Metro?Game=FoxGame.FoxGameMP_KC?NumBots=15?port=7777
```

Parameters are listed on [BL:RE's wiki](https://blrevive.gitlab.io/wiki/guides/hosting/game-server/parameters.html#blrevive-parameters).

## Future plans

* An agent that manages game state (start, monitoring, crash handling, etc...)
  * *Maybe* a "download game from steam and patch if not there" function in said agent, only if it doesn't bloat it too much
* A (web?) API allowing priviledged actions such as restarts, gamemode changes, etc...
  * An external Discord bot pluggeable to said API to allow gamemode changes votes
