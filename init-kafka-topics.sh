#!/bin/bash
set -e

echo "Waiting for Kafka to be ready..."
# Ждем пока Kafka станет доступной
while ! kafka-topics.sh --list --bootstrap-server kafka:9092 >/dev/null 2>&1; do
  sleep 5
done

echo "Creating topics..."
# Создаем топики с явным указанием всех параметров
topics=(
  "user-topic:3:1"
  "playlist-topic:3:1"
  "listening-history-topic:3:1"
  "application-logs:3:1"
)

for topic in "${topics[@]}"; do
  IFS=':' read -r name partitions replication <<< "$topic"
  
  echo "Creating topic $name with $partitions partitions and replication $replication"
  kafka-topics.sh --create \
    --bootstrap-server kafka:9092 \
    --topic "$name" \
    --partitions "$partitions" \
    --replication-factor "$replication" \
    --if-not-exists
done

echo "Topics created:"
kafka-topics.sh --list --bootstrap-server kafka:9092