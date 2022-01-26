import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import app


db = SQLAlchemy(app)


def get_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Snippets(db.Model):
    __tablename__ = "snippets"
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.Integer, db.ForeignKey("languages.id"))
    language_relation = db.relationship("Languages",
                                        backref=db.backref("snippets", lazy="dynamic"))
    description = db.Column(db.String(265), unique=True)
    snippet = db.Column(db.Text(4098), unique=True)
    comment = db.Column(db.String(265))
    created = db.Column(db.String(30))
    modified = db.Column(db.String(30))
    accessed = db.Column(db.String(30))
    visits = db.Column(db.Integer)

    def __init__(self, language_relation, description, snippet, comment):
        self.language = language_relation
        self.description = description
        self.snippet = snippet
        self.comment = comment
        self.created = get_time_str()
        self.modified = ""
        self.accessed = ""
        self.visits = 0

    def __repr__(self):
        return "[Snippet #%s]" % self.id

    def __str__(self):
        return json.dumps(self, indent=4, sort_keys=True)


class Languages(db.Model):
    __tablename__ = "languages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "[Language #%s]" % self.id

    def __str__(self):
        return json.dumps(self, indent=4, sort_keys=True)


@app.before_first_request
def startup():
    db.create_all()
    db.session.commit()
