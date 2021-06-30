from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os, uuid, math, random
import re
import connect
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import Flask
db=connect.db
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)
    # OneToMany
    articles = db.relationship('Article', backref='author')
    comments = db.relationship('Comment', backref='author')


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    pid = db.Column(db.Integer)
    # OneToMany
    articles = db.relationship('Article', backref='subject')


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    highlight = db.Column(db.Text)
    time = db.Column(db.DateTime)
    visit = db.Column(db.Integer)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)
    metric = db.Column(db.Float, default=0)
    fpath = db.Column(db.String)
    status = db.Column(db.Integer, default=1)
    # Add downloads
    downloadcount = db.Column(db.Integer)
    # OneToMany
    comments = db.relationship('Comment', backref='article', cascade='all,delete-orphan')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    body = db.Column(db.Text)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)
    time = db.Column(db.DateTime)


# ------------------------------------------------------#
#              record every visitor's ip               #
# ------------------------------------------------------#
class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)
    # OneToMangy
    article_votes = db.relationship('ArticleVote', backref='visitor')
    comment_votes = db.relationship('CommentVote', backref='visitor')
    visit_votes = db.relationship('VisitVote', backref='visitor')


class ArticleVote(db.Model):
    __tablename__ = 'article_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    article_id = db.Column(db.Integer)


class CommentVote(db.Model):
    __tablename__ = 'comment_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    comment_id = db.Column(db.Integer)


class VisitVote(db.Model):
    _tablename__ = 'visit_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    article_id = db.Column(db.Integer)


class SensitiveWord(db.Model):
    __tablename__ = 'sensitive_words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))


class Admin(db.Model):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)