import secrets
import string

import requests
from celery import shared_task
from flask import current_app
from sqlalchemy.orm import Session

from .extensions import db
from .models import Crawl


@shared_task()
def process_crawl(crawl_id: int):
    """
    Process a crawl task asynchronously.

    :param crawl_id: The ID of the crawl to process.
    :return: None
    """
    update_crawl_status(crawl_id, status='Running')
    current_app.logger.info(f'Starting crawl {crawl_id}')
    try:
        url = get_crawl_url(crawl_id)
        response = requests.get(url)
        if response.status_code == 200:
            # here is the HTML, it can be stored anywhere (AWS/GCP/Azure/etc).
            html = response.text

            update_crawl_status(crawl_id, status='Complete')

            # so I've mocked it with a path://<random_string>
            mock_save_html(crawl_id)
            return
    except Exception as e:
        pass
    update_crawl_status(crawl_id, status='Error')


def create_crawl(url: str) -> int:
    """
    Create a new crawl.

    :param url: The URL to crawl.
    :return: The ID of the created crawl.
    """
    crawl = Crawl(url=url, status='Accepted')
    with Session(db.engine) as session:
        session.add(crawl)
        session.commit()
        return crawl.id


def get_crawl(crawl_id: int) -> Crawl:
    """
    Get a crawl by its ID.

    :param crawl_id: The ID of the crawl.
    :return: The retrieved crawl.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).get(crawl_id)
        return crawl


def get_crawl_url(crawl_id: int) -> str:
    """
    Get the URL of a crawl by its ID.

    :param crawl_id: The ID of the crawl.
    :return: The URL of the crawl.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).get(crawl_id)
        return crawl.url


def update_crawl_status(crawl_id: int, status: str) -> int:
    """
    Update the status of a crawl.

    :param crawl_id: The ID of the crawl.
    :param status: The new status.
    :return: The ID of the updated crawl.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).get(crawl_id)
        crawl.status = status
        session.commit()
        return crawl.id


def mock_save_html(crawl_id: int) -> int:
    """
    Mock saving the HTML of a crawl.

    :param crawl_id: The ID of the crawl.
    :return: The ID of the crawl.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).get(crawl_id)
        crawl.html = generate_random_string()
        session.commit()
        return crawl.id


def generate_random_string() -> str:
    """
    Generate a random string.

    :return: The generated random string.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(50))
    return f'path://{random_string}'
