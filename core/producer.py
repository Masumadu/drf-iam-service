import json

from django.conf import settings
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from core.exceptions import AppException


def json_serializer(data):
    return json.dumps(data).encode("UTF-8")


def get_partition(key, all, available):
    return 0


def on_success(value):
    logger.info(f"{value} successfully published to topic {value.topic}")


def on_error(exc):
    logger.error(f"{exc} occurred while publishing to kafka")


def publish_to_kafka(topic, value):
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split("|"),
            value_serializer=json_serializer,
            partitioner=get_partition,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-256",
            sasl_plain_username=settings.KAFKA_SERVER_USERNAME,
            sasl_plain_password=settings.KAFKA_SERVER_PASSWORD,
        )
        producer.send(topic=topic, value=value).add_callback(on_success).add_errback(
            on_error
        )
        return True
    except KafkaError as exc:
        raise AppException.InternalServerException(
            error_message=f"KafkaError({exc})"
        ) from exc
