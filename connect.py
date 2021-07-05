from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os, uuid, math, random
import re
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import Flask
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir + '/static/pdf'
ALLOWED_EXTENSIONS = set(['pdf'])
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(basedir+'/static/pdf')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir+'/database.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
db = SQLAlchemy(app)
IP = '168.0.0.10'