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
	"github.com/fsnotify/fsnotify"
	"github.com/nxadm/tail"
	log "github.com/sirupsen/logrus"
)

type config struct {
	LogLevel     string `env:"BLREVIVE_LOGLEVEL" envDefault:"info"`
	Executable   string `env:"BLREVIVE_EXECUTABLE" envDefault:"BLR.exe"`
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

	GamePath := "/mnt/blacklightre"
	ExecutablePath := filepath.Join(GamePath, "Binaries/Win32", cfg.Executable)

	StartBlre(ExecutablePath, ServerOptions)

	wg.Add(1)
	go HandleLogs(GamePath)

	// Wait til routines are done running
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
	// Wine seemingly adds backslashes to argument's quotes (they are not there in ps axuf output but the server binary do get it)
	// To say this is annoying would be an understatement
	ServerOptionsArray = append(ServerOptionsArray, fmt.Sprintf("?Servername=%s", strings.ReplaceAll(cfg.ServerName, " ", "_")))
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

// Start xvfb
func StartXvfb() {
	// Very hack-y statement to free the Xvfb lock if the container was restarted before Xvfb freed it
	err := os.Remove("/tmp/.X9874-lock")
	if err != nil {
		log.WithField("display", ":9874").Trace("No Xvfb lock file to report")
	} else {
		log.WithField("display", ":9874").Warn("Had to remove a Xvfb lock file")
	}
	// Would be nice to use -displayfd instead of an arbitrary display number I suppose:
	XvfbCmd := exec.Command("Xvfb", ":9874", "-screen", "0", "1024x768x16")

	// Would be something like:
	// f, err := os.OpenFile("/tmp/xvfb", os.O_RDWR|os.O_CREATE, 0755)
	// if err != nil {
	// 		log.Fatal(err)
	// }
	// XvfbCmd := exec.Command("Xvfb", "-displayfd", "3", "-screen", "0", "1024x768x16")
	// XvfbCmd.ExtraFiles = []*os.File{f}

	// Matter is that it removes reliance on /tmp/.X9874-lock to rely on /tmp/xvfb instead... Not quite optimal.

	StartProcessAndScan(XvfbCmd)

	os.Setenv("DISPLAY", ":9874")
	log.WithField("display", ":9874").Debug("Started Xvfb successfully")
}

// Start the game
func StartBlre(ExecutablePath string, ServerOptions string) {
	GameCmd := exec.Command("wine", ExecutablePath, "server", ServerOptions)

	StartProcessAndScan(GameCmd)
}

// Spawn a new process and pipe its stdout/stderr to the entrypoint's logs
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

	wg.Add(1)
	go func() {
		Cmd.Wait()
		log.WithFields(log.Fields{
			"process":  ProcessName,
			"exitcode": Cmd.ProcessState.ExitCode(),
		}).Fatal("Subprocess died! Aborting...")
		wg.Done()
	}()
}

// Watch for new files in the predetermined log folder and output them through the entrypoint's log
func HandleLogs(GamePath string) {
	defer wg.Done()

	// Create fsnotify watcher
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.WithField("process", "entrypoint").Error(err)
	}
	defer watcher.Close()

	logPath := filepath.Join(GamePath, "FoxGame/Logs")

	done := make(chan bool)

	wg.Add(1)
	go func() {
	watchloop:
		for {
			select {
			case event := <-watcher.Events:
				log.WithFields(log.Fields{
					"logpath": logPath,
					"event":   event,
				}).Trace("New fsnotify event in log folder")

				if event.Op == fsnotify.Create {
					log.WithFields(log.Fields{
						"process": "entrypoint",
						"logfile": filepath.Base(event.Name),
					}).Info("A new file was created in the log folder")
					wg.Add(1)
					go TailLogToStdout(event.Name)
				}

			case err := <-watcher.Errors:
				log.WithField("process", "entrypoint").Error(err)
				break watchloop
			}
		}
		wg.Done()
	}()

	if err := watcher.Add(logPath); err != nil {
		log.WithField("process", "entrypoint").Error(err)
	}

	<-done
}

func TailLogToStdout(LogFile string) {
	defer wg.Done()

	t, err := tail.TailFile(
		LogFile, tail.Config{Follow: true, ReOpen: true, MustExist: true})
	if err != nil {
		log.WithField("logfile", filepath.Base(LogFile)).Error(err)
		return
	}

	for line := range t.Lines {
		log.WithField("logfile", filepath.Base(LogFile)).Info(line)
	}
}
