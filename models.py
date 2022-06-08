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


def get_username():
    return auth.current_user.get('username') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'image',
    Field('owner', default=get_user_email),
#    Field('image', 'upload', uploadfolder='apps/FinishMyArt/static/art'),
    Field('file_name'),
    Field('file_type'),
    Field('file_date'),
    Field('file_path'),
    Field('file_size', 'integer'),
    Field('is_post', 'boolean', default=False),
    Field('confirmed', 'boolean', default=False), # Was the upload to GCS confirmed?
)


db.define_table(
    'post',
    Field('owner', default=get_user_email),
    Field('title', length=100, requires=IS_NOT_EMPTY()),
    Field('description', 'text'),
    Field('is_child', 'boolean', default=False),
    Field('parent_post', 'reference post'),
    Field('image_id', 'reference image'),
    Field('in_progress', 'boolean', default = True),
)

db.define_table(
    'user_profile',
    Field('owner', default=get_user_email),
    Field('username', default=get_username),
    Field('description', 'text', length=120),
    Field('likes', 'integer', default=0),
    Field('image_id', 'reference image'),
    Field('banner_id', 'reference image'),
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
db.image.file_name.readable = db.image.file_name.writable = False
db.image.file_type.readable = db.image.file_type.writable = False
db.image.file_date.readable = db.image.file_date.writable = False
db.image.file_path.readable = db.image.file_path.writable = False
db.image.file_size.readable = db.image.file_size.writable = False


db.user_profile.owner.readable = db.post.owner.writable = False
db.like.owner.readable = db.post.owner.writable = False

db.define_table(
    'test',
    Field('image_url'),
    Field('description'),
)


db.commit()
