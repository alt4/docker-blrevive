package main

import (
	"testing"

	log "github.com/sirupsen/logrus"
)

type LogLevels struct {
	LevelString string
	LevelObject log.Level
}

var LogLevelTests = []LogLevels{
	{"trace", log.TraceLevel},
	{"TrAcE", log.TraceLevel},
	{"debug", log.DebugLevel},
	{"DEbUg", log.DebugLevel},
	{"info", log.InfoLevel},
	{"InFO", log.InfoLevel},
	{"randomvalue", log.InfoLevel},
}

func TestDetermineLogLevel(t *testing.T) {
	for i, test := range LogLevelTests {
		DetermineLogLevel(test.LevelString)
		if log.GetLevel() != test.LevelObject {
			t.Errorf("#%d: DetermineLogLevel(%s)=%s; expected %s", i, test.LevelString, log.GetLevel().String(), test.LevelObject)
		}
	}
}

type ServerOptions struct {
	Configuration  config
	ExpectedString string
}

var ServerOptionsTests = []ServerOptions{
	{
		Configuration: config{
			ServerName: "BLREvive Docker Server",
			Map:        "HeloDeck",
		},
		ExpectedString: "HeloDeck?Servername=BLREvive_Docker_Server",
	},
	{
		Configuration: config{
			ServerName:   "a server",
			GamePassword: "password",
			Map:          "HeloDeck",
			GameMode:     "KC",
			Playlist:     "KC",
			MaxPlayers:   "8",
			NumBots:      "3",
			TimeLimit:    "300",
			SCP:          "400",
		},
		ExpectedString: "HeloDeck?Servername=a_server?GamePassword=password?Playlist=KC?Game=FoxGame.FoxGameMP_KC?NumBots=3?MaxPlayers=8?TimeLimit=300?SCP=400",
	},
}

func TestDetermineServerOptions(t *testing.T) {
	for i, test := range ServerOptionsTests {
		ServerOptions := DetermineServerOptions(test.Configuration)
		if ServerOptions != test.ExpectedString {
			t.Errorf("#%d: DetermineLogLevel(%+v)=%s; expected %s", i, test.Configuration, ServerOptions, test.ExpectedString)
		}
	}
}
