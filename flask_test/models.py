from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_ko = db.Column(db.String(64))
    company_en = db.Column(db.String(64))
    company_ja = db.Column(db.String(64))
    tag_ko = db.Column(db.String(64))
    tag_en = db.Column(db.String(64))
    tag_ja = db.Column(db.String(64))
