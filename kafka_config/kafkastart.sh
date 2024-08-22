#!/bin/sh

/opt/kafka/bin/kafka-configs.sh --zookeeper kafka:2181 --alter --add-config 'SCRAM-SHA-256=[password=admin-secret],SCRAM-SHA-512=[password=admin-secret]' --entity-type users --entity-name admin &&
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
