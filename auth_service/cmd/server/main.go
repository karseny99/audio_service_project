package main

import (
	"fmt"
	k "github.com/karseny99/audio_service_project/auth_service/internal/kafka/producer"
	"github.com/sirupsen/logrus"
)

const (
	topic = "my-awesome-topic"
)

var address = []string{"localhost:9091", "localhost:9092"}

func main() {

	p, err := k.NewProducer(address)
	if err != nil {
		logrus.Fatal(err.Error())
	}

	for i := 0; i < 100; i++ {
		msg := fmt.Sprintf("Hello world %d", i)
		if err = p.Produce(msg, topic); err != nil {
			logrus.Fatal(err.Error())
		}
	}
}
