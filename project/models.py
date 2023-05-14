from .extensions import db


class Crawl(db.Model):
    __tablename__ = 'crawl'

    id = db.Column(db.Integer, primary_key=True)
    crawl_hash = db.Column(db.String(100), index=True)
    status = db.Column(db.String(15))
    task_id = db.Column(db.String(100))
    url = db.Column(db.String(100))
    html = db.Column(db.String(500))
