"""Celery app. Broker and result backend from config."""
from celery import Celery
from app.config import get_config


def make_celery() -> Celery:
    config = get_config()
    celery = Celery(
        "ttn_oj",
        broker=config.celery_broker_url,
        backend=config.celery_result_backend,
        include=["app.tasks.judge_task"],
    )
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return celery


celery_app = make_celery()
