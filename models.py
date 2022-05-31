"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'post',
    Field('title', length=100, requires=IS_NOT_EMPTY()),
    Field('desc', 'text'),
    Field('image', 'upload', uploadfolder='apps/fma/static/art'),
    Field('created_by', default=get_user_email)
)

db.post.id.readable = db.post.id.writable = False
db.post.created_by.readable = db.post.created_by.writable = False

db.define_table(
    'profile',
    Field('username'),
    Field('description'),
)

db.commit()
