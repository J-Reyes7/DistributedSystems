#!/bin/bash -e

exec "/kafka/bin/zookeeper-server-start.sh" "/kafka/config/zookeeper.properties"

exec "/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper-1:2181 --replication-factor 3 --partitions 2 --topic Apple"

exec "/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper-1:2181 --replication-factor 1 --partitions 1 --topic Lyft"

exec "/kafka/bin/kafka-topics.sh --create --zookeeper zookeeper-1:2181 --replication-factor 1 --partitions 1 --topic Amazon"
