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
    Field('file_name'),
    Field('file_type'),
    Field('file_date'),
    Field('file_path'),
    Field('file_size', 'integer'),
    Field('confirmed', 'boolean', default=False),
)

db.define_table(
    'post',
    Field('owner', default=get_user_email),
    Field('title', length=100, requires=IS_NOT_EMPTY()),
    Field('description','text'),
    Field('is_child', 'boolean', default=False),
    Field('parent_post', 'reference post'),
    Field('image_id', db.image),
    Field('image', 'upload', uploadfolder='apps/fma/static/art'),
)

db.define_table(
    'user_profile',
    Field('owner', default=get_user_email),
    Field('username', default=get_username),
    Field('description', 'text', length=120),
    Field('likes', 'integer', default=0),
    Field('image_id', 'reference image'),
)

db.define_table(
    'like',
    Field('owner', default=get_user_email),
    Field('likes', 'boolean'),
    Field('post_id', 'reference post'),
)

db.post.owner.readable = db.post.owner.writable = False
db.post.id.readable = False 
db.post.image_id.readable = db.post.image_id.writable = False
db.image.id.readable = False 
db.image.owner.readable = db.image.owner.writable = False

db.user_profile.owner.readable = db.post.owner.writable = False
db.like.owner.readable = db.post.owner.writable = False

db.define_table(
    'test',
    Field('image_url'),
    Field('description'),
)


db.commit()

