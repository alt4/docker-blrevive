package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"

	"github.com/caarlos0/env/v7"
	log "github.com/sirupsen/logrus"
)

type config struct {
	LogLevel     string `env:"BLREVIVE_LOGLEVEL" envDefault:"info"`
	ServerName   string `env:"BLREVIVE_GAME_SERVERNAME" envDefault:"BLREvive Docker Server"`
	GamePassword string `env:"BLREVIVE_GAME_GAMEPASSWORD,unset"`
	Map          string `env:"BLREVIVE_GAME_MAP" envDefault:"HeloDeck"`
	GameMode     string `env:"BLREVIVE_GAME_GAMEMODE"`
	Playlist     string `env:"BLREVIVE_GAME_PLAYLIST"`
	MaxPlayers   string `env:"BLREVIVE_GAME_MAXPLAYERS"`
	NumBots      string `env:"BLREVIVE_GAME_NUMBOTS"`
	TimeLimit    string `env:"BLREVIVE_GAME_TIMELIMIT"`
	SCP          string `env:"BLREVIVE_GAME_SCP"`
}

var wg sync.WaitGroup

func init() {
	log.SetOutput(os.Stdout)
}

func main() {
	log.Info("Starting BLREvive...")

	cfg := config{}
	if err := env.Parse(&cfg); err != nil {
		log.Errorf("%+v\n", err)
	}

	DetermineLogLevel(cfg.LogLevel)

	log.WithField("config", fmt.Sprintf("%+v", cfg)).Tracef("Parsed env vars")

	ServerOptions := DetermineServerOptions(cfg)

	log.WithField("options", ServerOptions).Debug("Parsed server options")

	StartXvfb()

	StartBlre(ServerOptions)

	wg.Wait()
}

func DetermineLogLevel(LogLevel string) {
	switch logLevel := LogLevel; strings.ToLower(logLevel) {
	case "trace":
		log.SetLevel(log.TraceLevel)
	case "debug":
		log.SetLevel(log.DebugLevel)
	case "info":
		log.SetLevel(log.InfoLevel)
	default:
		log.SetLevel(log.InfoLevel)
	}
}

func DetermineServerOptions(cfg config) string {
	// They said you should keep it simple, so I did
	// I still miss this abomination https://gitlab.com/northamp/docker-blrevive/-/blob/3ed14f4fd5590643fe6df77e7066f215914f2dc0/src/mars/launcher.py#L38
	var ServerOptionsArray []string

	ServerOptionsArray = append(ServerOptionsArray, cfg.Map)
	for i, word := range strings.Split(cfg.ServerName, " ") {
		if i == 0 {
			ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?Servername=%s", word))
		} else {
			ServerOptionsArray = append(ServerOptionsArray, " "+word)
		}
	}
	if cfg.GamePassword != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?GamePassword=%s", cfg.GamePassword))
	}
	if cfg.Playlist != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?Playlist=%s", cfg.Playlist))
	}
	if cfg.GameMode != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?Game=FoxGame.FoxGameMP_%s", cfg.GameMode))
	}
	if cfg.NumBots != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?NumBots=%s", cfg.NumBots))
	}
	if cfg.MaxPlayers != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?MaxPlayers=%s", cfg.MaxPlayers))
	}
	if cfg.TimeLimit != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?TimeLimit=%s", cfg.TimeLimit))
	}
	if cfg.SCP != "" {
		ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?SCP=%s", cfg.SCP))
	}

	return strings.Join(ServerOptionsArray, "")
}

func StartXvfb() {
	// Would be nice to use -displayfd instead of an arbitrary display number I suppose
	XvfbCmd := exec.Command("Xvfb", ":9874", "-screen", "0", "1024x768x16")

	StartProcessAndScan(XvfbCmd)

	os.Setenv("DISPLAY", ":9874")
	log.WithField("display", ":9874").Debug("Started xvfb successfully")
}

func StartBlre(ServerOptions string) {
	GamePath := "/mnt/blacklightre"
	GameExecutable := "Binaries/Win32/BLR.exe"
	ExecutablePath := filepath.Join(GamePath, GameExecutable)
	GameCmd := exec.Command("wine", ExecutablePath, "server", ServerOptions)

	StartProcessAndScan(GameCmd)
}

func StartProcessAndScan(Cmd *exec.Cmd) {
	ProcessName := filepath.Base(Cmd.Path)
	stdout, err := Cmd.StdoutPipe()
	if err != nil {
		log.WithField("process", ProcessName).Error(err)
	}

	stderr, err := Cmd.StderrPipe()
	if err != nil {
		log.WithField("process", ProcessName).Error(err)
	}

	if err := Cmd.Start(); err != nil {
		log.WithField("process", ProcessName).Fatal(err)
	}

	scannerStdout := bufio.NewScanner(stdout)
	wg.Add(1)
	go func() {
		for scannerStdout.Scan() {
			log.WithField("process", ProcessName).Infof(scannerStdout.Text())
		}
		wg.Done()
	}()

	scannerStderr := bufio.NewScanner(stderr)
	wg.Add(1)
	go func() {
		for scannerStderr.Scan() {
			log.WithField("process", ProcessName).Errorf(scannerStderr.Text())
		}
		wg.Done()
	}()

	go func() {
		Cmd.Wait()
		log.WithFields(log.Fields{
			"process":  ProcessName,
			"exitcode": Cmd.ProcessState.ExitCode(),
		}).Fatal("Subprocess died! Aborting...")
	}()
}
