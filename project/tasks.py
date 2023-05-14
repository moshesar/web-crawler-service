import secrets
import string
from hashlib import sha256

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
    Create a new crawl (if it's not yet exist - by hash).

    :param url: The URL to crawl.
    :return: The ID of the created crawl.
    """
    crawl_hash = compute_crawl_hash(url)

    # Check if the crawl hash already exists
    existing_crawl = get_crawl_by_hash(crawl_hash)
    if existing_crawl:
        return existing_crawl.id

    crawl = Crawl(url=url, status='Accepted', crawl_hash=crawl_hash)
    with Session(db.engine) as session:
        session.add(crawl)
        session.commit()
        process_crawl.delay(crawl.id)
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


def get_crawl_hash(crawl_id: int) -> str:
    """
    Get the crawl hash of a crawl by its ID.

    :param crawl_id: The ID of the crawl.
    :return: The crawl hash.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).get(crawl_id)
        return crawl.crawl_hash


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


def compute_crawl_hash(url: str) -> str:
    """
    Compute the crawl hash for a given URL.

    :param url: The URL to compute the crawl hash for.
    :return: The computed crawl hash.
    """
    return sha256(url.encode()).hexdigest()


def get_crawl_by_hash(crawl_hash: str) -> Crawl:
    """
    Get a crawl by its hash.

    :param crawl_hash: The crawl hash.
    :return: The retrieved crawl.
    """
    with Session(db.engine) as session:
        crawl = session.query(Crawl).filter_by(crawl_hash=crawl_hash).first()
        return crawl


def generate_random_string() -> str:
    """
    Generate a random string.

    :return: The generated random string.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(50))
    return f'path://{random_string}'
