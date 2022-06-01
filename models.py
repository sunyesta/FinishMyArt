"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None
def get_username():
    return auth.current_user.get('username') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'image',
    Field('owner', default=get_user_email),
    Field('image', 'upload', uploadfolder='apps/fma/static/art'),
    Field('file_name'),
    Field('file_type'),
    Field('file_date'),
    Field('file_path'),
    Field('file_size', 'integer'),
)

db.define_table(
    'post',
    Field('owner', default=get_user_email),
    Field('title', length=100, requires=IS_NOT_EMPTY()),
    Field('description'),
    Field('is_child', 'boolean', default=False),
    Field('parent_post', 'reference post'),
    Field('image_id', 'reference image'),
)

db.define_table(
    'user_profile',
    Field('owner', default=get_user_email),
    Field('username', default=get_username),
    Field('description','text', length=120),
    Field('likes', 'integer', default=0),
    Field('image_id', 'reference image'),
)

db.define_table(
    'like',
    Field('owner', default=get_user_email),
    Field('likes', 'boolean'),
    Field('post_id', 'reference post'),
)



db.post.created_by.readable = db.post.created_by.writable = False

db.commit()
