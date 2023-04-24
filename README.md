# BLRevive Docker Server

<!-- markdownlint-disable-next-line MD033 -->
<img title="M.A.R.S. doodle. These Wine builds take ages, man" align="right" height="275" width="330" src="https://gitlab.com/northamp/docker-blrevive/-/raw/master/mars.png" >

A Docker implementation of the [Blacklight: Retribution Revive](https://gitlab.com/blrevive) server.

Comes with a Golang launcher script allowing control over the server's settings and status.

**NOTE**: Requires a dual-core processor due to a BL:R warning that cannot be acknowledged on headless instances (yet). Also, while it seems promising, performance wasn't thoroughly evaluated yet. Use at your own risks!

## Usage

The game's files need to be mounted to `/mnt/blacklightre/`. Rest of the `README` will assume they're located on the host's `/srv/blacklightre`.

```bash
docker run --rm -v /srv/blacklightre/:/mnt/blacklightre --env BLREVIVE_GAME_NUMBOTS=2 -p 5000:5000 -p 7777:7777/udp registry.gitlab.com/northamp/docker-blrevive:latest
```

### Downloading the game

Downloading Blacklight can be done entirely on Docker using DepotDownloader.

The only pre-requisite is a Steam account that can download BLR:

**NOTE**: The [filelist](https://gitlab.com/-/snippets/2529720/raw/main/filelist.txt) is used to prevent downloading `.tfc` files and save nearly 4GB of space. Comment the curl command and the `-filelist` argument if you intend to run a client.

```bash
STEAM_USERNAME=YOU!
docker run -it -v /srv/blacklightre/:/mnt/blacklightre/ mcr.microsoft.com/dotnet/sdk:6.0 bash -c "apt-get update \
  && apt-get install -y unzip \
  && curl -L -O https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.4.7/depotdownloader-2.4.7.zip \
  && unzip depotdownloader-2.4.7.zip \
  && curl -LO https://gitlab.com/-/snippets/2529720/raw/main/filelist.txt \
  && dotnet DepotDownloader.dll -app 209870 -username $STEAM_USERNAME -filelist filelist.txt \
  && mv depots/209871/2520205/ /mnt/blacklightre/"
```

Applying BL:RE's patch is going to be more finicky: current launcher releases do not support CLI patching properly.

Your best bet is patching the game manually elsewhere and copying the binaries to `/srv/blacklightre/Binaries/Win32`.

### Server settings

Startup server settings can be overriden using the following environment variables:

| Name                       | Description                                                                    | Default                  |
| -------------------------- | ------------------------------------------------------------------------------ | ------------------------ |
| `BLREVIVE_LOGLEVEL`        | Set to `debug` or `trace` for more logs from the entrypoint                    | `info`                   |
| `BLREVIVE_EXECUTABLE`      | Patched executable name                                                        | `BLR.exe`                |
| `BLREVIVE_GAME_SERVERNAME` | Server name                                                                    | `BLREvive Docker Server` |
| `BLREVIVE_GAME_PASSWORD`   | Password clients should provide to enter                                       | ``                       |
| `BLREVIVE_GAME_MAP`        | Initial Map, will be rotated by playlist. Check the wiki for more informations | `HeloDeck`               |
| `BLREVIVE_GAME_GAMEMODE`   | Gamemode, will be rotated by playlist. Check the wiki for more informations    | ``                       |
| `BLREVIVE_GAME_PLAYLIST`   | Server playlist                                                                | ``                       |
| `BLREVIVE_GAME_NUMBOTS`    | Number of bots                                                                 | ``                       |
| `BLREVIVE_GAME_MAXPLAYERS` | Maximum amount of players allowed                                              | ``                       |
| `BLREVIVE_GAME_TIMELIMIT`  | Time limit for each rounds                                                     | ``                       |
| `BLREVIVE_GAME_SCP`        | Amount of SCP players start with                                               | ``                       |

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
      - BLREVIVE_DEBUG="debug"
      - BLREVIVE_GAME_SERVERNAME="And all I got was this lousy dock"
      - BLREVIVE_GAME_PLAYLIST="KC"
      - BLREVIVE_GAME_NUMBOTS="2"
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
  BLREVIVE_DEBUG: "debug"
  BLREVIVE_GAME_SERVERNAME: "And all I got was this lousy kube"
  BLREVIVE_GAME_PLAYLIST: "KC"
  BLREVIVE_GAME_NUMBOTS: "2"
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

### Kubernetes (with server-utils)

Mounting server-utils' configuration requires using an initcontainer if you want to keep the game's volume read-only.

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
apiVersion: v1
kind: ConfigMap
metadata:
  name: blrevive-serverutils-config
  namespace: blrevive
  labels:
    app: blrevive
data:
  server-utils.config: |
    {
        "hacks": {
            "disableOnMatchIdle": 1
        },
        "properties": {
            "GameForceRespawnTime": 30.0,
            "GameRespawnTime": 3.0,
            "GameSpectatorSwitchDelayTime": 120.0,
            "GoalScore": 3000,
            "MaxIdleTime": 180.0,
            "MinRequiredPlayersToStart": 1,
            "NumEnemyVotesRequiredForKick": 4,
            "NumFriendlyVotesRequiredForKick": 2,
            "PlayerSearchTime": 30.0,
            "RandomBotNames": [
                "bot",
                "tob",
                "49494",
                "878978",
                "46464",
                "56464465",
                "4565456",
                "545485",
                "5454",
                "4987498",
                "9787",
                "1",
                "12",
                "11",
                "910",
                "78",
                "56",
                "34",
                "12"
            ],
            "TimeLimit": 10,
            "VoteKickBanSeconds": 1200
        }
    }
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
      initContainers:
      - name: server-utils-config
        image: busybox
        command: ['/bin/sh', '-c', 'cp /tmp/server_config.json /mnt/server_utils']
        volumeMounts:
          - name: blrevive-serverutils-dir
            mountPath: /mnt/server_utils
          - name: blrevive-serverutils-config
            mountPath: /tmp/server_config.json
            subPath: server_config.json
      containers:
      - name: blrevive
        image: registry.gitlab.com/northamp/docker-blrevive:latest
        imagePullPolicy: Always
        envFrom:
          - configMapRef:
              name: blrevive-config
        # Wine debug messages
        # env:
        #   - name: WINEDEBUG
        #     value: "warn+all,+loaddll"
        ports:
        - name: game
          containerPort: 7777
          protocol: UDP
        - name: api
          containerPort: 7778
          protocol: TCP
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
          - mountPath: /mnt/blacklightre/FoxGame/Logs
            name: blrevive-logs
          - mountPath: /mnt/blacklightre/FoxGame/Config/BLRevive/server_utils
            name: blrevive-serverutils-dir
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      volumes:
        - name: blrevive-gamefiles
          persistentVolumeClaim:
            claimName: blrevive-pv-claim
        - name: blrevive-logs
          emptyDir: {}
        - name: blrevive-serverutils-dir
          emptyDir: {}
        - name: blrevive-serverutils-config
          configMap:
            name: blrevive-serverutils-config
            items: 
              - key: server-utils.config
                path: server_config.json
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
---
apiVersion: v1
kind: Service
metadata:
  name: blrevive-api
  namespace: blrevive
  labels:
    app: blrevive
spec:
  ports:
  - name: api
    port: 80
    targetPort: api
    protocol: TCP
  selector:
    app: blrevive
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blrevive-ingress-insecure
  namespace: blrevive
  annotations:
    kubernetes.io/ingress.class: "traefik"
spec:
  rules:
  - host: blrevive.example.com
    http:
      paths:
      - backend:
          service:
            name: blrevive-api
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blrevive-ingress
  namespace: blrevive
  annotations:
    kubernetes.io/ingress.class: "traefik"
    traefik.ingress.kubernetes.io/router.tls: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: blrevive.example.com
    http:
      paths:
      - backend:
          service:
            name: blrevive-api
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
  tls:
  - hosts:
    - blrevive.example.com
    secretName: blrevive-example-com-tls
```

## Credits/Acknowledgements

### Wine build

Though the CI and imaging processes are now different, they are essentially based on [pg9182/northstar-dedicated](https://github.com/pg9182/northstar-dedicated/)'s excellent zlib/libpng licensed project.

### MagicCow

Previous versions up to the Golang entrypoint rewrite were similar to [MagicCow's MIT licensed Discord bot](https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot).
