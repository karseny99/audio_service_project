package producer

import (
	"errors"
	"fmt"
	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"strings"
)

const (
	flushTimeout = 5000 // ms
)

var unknownErr = errors.New("unknown event type")

type Producer struct {
	producer *kafka.Producer
}

func NewProducer(addrs []string) (*Producer, error) {
	conf := &kafka.ConfigMap{
		"bootstrap.servers": strings.Join(addrs, ","),
	}

	producer, err := kafka.NewProducer(conf)
	if err != nil {
		return nil, fmt.Errorf("failed to create kafka producer: %w", err)
	}

	return &Producer{producer: producer}, nil
}

func (p *Producer) Produce(message, topic string) error {
	kafkaMsg := &kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &topic,
			Partition: kafka.PartitionAny,
		},
		Value: []byte(message),
		Key:   nil,
	}
	kafkaCh := make(chan kafka.Event)
	if err := p.producer.Produce(kafkaMsg, kafkaCh); err != nil {
		return fmt.Errorf("failed to produce message: %w", err)
	}

	event := <-kafkaCh
	switch ev := event.(type) {
	case *kafka.Message:
		return nil
	case *kafka.Error:
		return ev
	default:
		return unknownErr
	}
}

func (p *Producer) Close() {
	p.producer.Flush(flushTimeout)
	p.producer.Close()
}
