# M.A.R.S A.P.I.

Some sort of RCON, until we get an "official" master server.

Tested on Werkzeug and Gunicorn.

## Quickstart

Either run it with the launcher script as such:

```bash
python3 launcher.py -a 0.0.0.0 -p 5000
```

Or, preferably, with Gunicorn:

```bash
gunicorn -w 1 -b 0.0.0.0:5000 api
```
