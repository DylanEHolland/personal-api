from backend import db
from datetime import datetime
import os


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __init__(self, **data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get('email')

    def commit(self):
        db.session.add(self)
        db.session.commit()


class WikiPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.Integer, db.ForeignKey('member.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    page_content = db.Column(db.Text)
    title = db.Column(db.Text)
    url = db.Column(db.Text, unique=True)

    def __init__(self, **data):
        self.title = data.get('title')
        self.url = data.get('url')
        self.page_content = data.get('page_content')
        self.creator = data.get('creator')

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.page_content,
            'url': self.url
        }


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    page_id = db.Column(db.Integer, db.ForeignKey('wiki_page.id'))
    image_url = db.Column(db.String)

    def __init__(self, **data):
        self.page_id = data.get('page_id')
        self.image_url = data.get('image_url')

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'page_id': self.page_id,
            'image_url': self.image_url
        }


class PageEditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    editor = db.Column(db.Integer, db.ForeignKey('member.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('wiki_page.id'))

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self, **data):
        self.editor = data.get('editor')
        self.page_id = data.get('page_id')


db.create_all()
print(f"Using database: {os.environ.get('DATABASE_URL')}")
