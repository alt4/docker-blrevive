# BLRevive Docker Server

<img title="M.A.R.S. doodle. These Wine builds take ages, man" align="right" height="275" width="330" src="https://gitlab.com/northamp/docker-blrevive/-/raw/master/marsapi.png" >

A Docker implementation of the [Blacklight: Retribution Revive](https://gitlab.com/blrevive) server.

Comes with a Python launcher script allowing control over the server's settings and status.

**NOTE**: Requires a dual-core processor due to a BL:R warning that cannot be acknowledged on headless instances (yet). Also, while it seems promising, performance wasn't thoroughly evaluated yet. Use at your own risks!

## Usage

The game's files need to be mounted to `/mnt/blacklightre/`. Rest of the `README` will assume they're located on the host's `/srv/blacklightre`.

```bash
docker run --rm -v /srv/blacklightre/:/mnt/blacklightre --env MARS_GAME_NUMBOTS=2 -p 5000:5000 -p 7777:7777/udp registry.gitlab.com/northamp/docker-blrevive:latest
```

### Downloading the game

Downloading Blacklight can be done entirely on Docker using DepotDownloader.

The only pre-requisite is a Steam account that can download BLR:

```bash
STEAM_USERNAME=YOU!
docker run -it -v /srv/blacklightre/:/mnt/blacklightre/ mcr.microsoft.com/dotnet/sdk:6.0 bash -c "apt-get update \
  && apt-get install -y unzip \
  && curl -L -O https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.4.7/depotdownloader-2.4.7.zip \
  && unzip depotdownloader-2.4.7.zip \
  && dotnet DepotDownloader.dll -app 209870 -username $STEAM_USERNAME \
  && mv depots/209871/2520205/ /mnt/blacklightre/"
```

Applying BL:RE's patch is going to be more finicky: current launcher releases do not support CLI patching properly.

Your best bet is patching the game manually elsewhere and copying the binaries to `/srv/blacklightre/Binaries/Win32`.

### Server settings

Startup server settings can be overriden using the following environment variables:

| Name                      | Description                                                                                                      | Default                                     |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| `MARS_DEBUG`              | Set to any value to enable verbose logging                                                                       | ``                                          |
| `MARS_SERVER_EXE`         | Server executable name mounted to the container, should be located in `/srv/blacklightre/Binaries/Win32/<exe>`   | `FoxGame-win32-Shipping-Patched-Server.exe` |
| `MARS_GAME_SERVERNAME`    | Server name                                                                                                      | `MARS Managed BLRE Server`                  |
| `MARS_GAME_MAP`           | Initial Map, will be rotated by playlist. Check the wiki for more informations                                   | `HeloDeck`                                  |
| `MARS_GAME_GAMEMODE`      | Gamemode, will be rotated by playlist. Check the wiki for more informations                                      | ``                                          |
| `MARS_GAME_PLAYLIST`      | Server playlist                                                                                                  | ``                                          |
| `MARS_GAME_NUMBOTS`       | Number of bots                                                                                                   | ``                                          |
| `MARS_GAME_MAXPLAYERS`    | Maximum amount of players allowed                                                                                | ``                                          |
| `MARS_GAME_TIMELIMIT`     | Time limit for each rounds                                                                                       | ``                                          |
| `MARS_GAME_SCP`           | Amount of SCP players start with                                                                                 | ``                                          |

Parameters are listed on [BL:RE's wiki](https://blrevive.gitlab.io/wiki/guides/hosting/game-server/parameters.html#blrevive-parameters).

## Deployment

Here's some sample deployment setups:

### Docker-Compose

```yaml
version: '3'
services:
  blrevive:
    image: registry.gitlab.com/northamp/docker-blrevive:latest
    restart: always
    environment:
      - MARS_DEBUG="True"
      - MARS_SERVER_EXE="FoxGame-win32-Shipping-Patched-Server.exe"
      - MARS_GAME_SERVERNAME="And all I got was this lousy dock"
      - MARS_GAME_PLAYLIST="KC"
      - MARS_GAME_NUMBOTS="2"
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: blrevive-config
  namespace: blrevive
  labels:
    app: blrevive
data:
  MARS_DEBUG: "True"
  MARS_SERVER_EXE: "FoxGame-win32-Shipping-Patched-Server.exe"
  MARS_GAME_SERVERNAME: "And all I got was this lousy kube"
  MARS_GAME_PLAYLIST: "KC"
  MARS_GAME_NUMBOTS: "2"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blrevive
  namespace: blrevive
  labels:
    app: blrevive
spec:
  replicas: 1
  selector:
    matchLabels:
      app: blrevive
  template:
    metadata:
      labels:
        app: blrevive
    spec:
      containers:
      - name: blrevive
        image: registry.gitlab.com/northamp/docker-blrevive:latest
        envFrom:
          - configMapRef:
              name: blrevive-config
        # Wine debug messages
        # env:
        #   - name: WINEDEBUG
        #     value: "warn+all"
        ports:
        - name: game
          containerPort: 7777
          protocol: UDP
        resources:
          requests:
            memory: "1024M"
            cpu: "0.25"
          limits:
            memory: "2048M"
            cpu: "2"
        volumeMounts:
          - mountPath: /mnt/blacklightre/
            name: blrevive-gamefiles
            readOnly: true
      volumes:
        - name: blrevive-gamefiles
          persistentVolumeClaim:
            claimName: blrevive-pv-claim
---
apiVersion: v1
kind: Service
metadata:
  name: blrevive-game
  namespace: blrevive
  labels:
    app: blrevive
spec:
  type: LoadBalancer
  ports:
  - name: game
    port: 7777
    targetPort: game
    protocol: UDP
  selector:
    app: blrevive
```

## Credits/Acknowledgements

### Wine build

Though the CI and imaging processes are now different, they are essentially based on [pg9182/northstar-dedicated](https://github.com/pg9182/northstar-dedicated/)'s excellent zlib/libpng licensed project.

### MagicCow

Bits of code (and the now defunct attempt at a REST API) are either identical or very similar to [MagicCow's MIT licensed Discord bot](https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot).

Reason not to use that in the image to begin with is the (current) lack of separation between the whole Cheat Engine thing (which isn't quite possible on Wine/Docker), the bot, and the REST API itself. The architecture I have in mind cannot quite fuse all of them in one. I'll most likely strive to maintain interoperability between the two when possible however.
