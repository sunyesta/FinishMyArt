"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""


import datetime
import json
import os
import traceback
import uuid
from xml.dom.pulldom import PROCESSING_INSTRUCTION
from nqgcs import NQGCS

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_username
from .settings import APP_FOLDER
from .gcs_url import gcs_url
from py4web.utils.form import Form, FormStyleBulma
from .common import Field
import datetime

url_signer = URLSigner(session)

# ---------Temp tables for testing--------
TESTDATA = ["happy_star.svg", "cat.jpg", "tokage.png"]


url_signer = URLSigner(session)

BUCKET = '/finishmyart-art'


GCS_KEY_PATH = os.path.join(
    APP_FOLDER, 'private/finishmyart-a7fc05f5fa13.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

# I create a handle to gcs, to perform the various operations.
gcs = NQGCS(json_key_path=GCS_KEY_PATH)


def do_setup():
    db(db.test).delete()
    for img in TESTDATA:
        db.test.insert(image_url=URL('static', 'assets/' + img),
                       description="hello")

# -----------------Index-----------------


@action('vueTemp')
@action.uses('vueTemp.html', db, auth, url_signer)
def vueTemp():
    return dict()

@action("orphans", method=["GET", "POST"])
@action.uses("orphans.html", auth.user)
def orphans():
    orphans = db(db.post.is_child == False).select()
    return orphans


@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    user = auth.get_user()
    posts = db(db.post).select()
    return dict(
        email = get_user_email(),
        posts=posts,
        orphans_url = URL('orphans', signer=url_signer),
        add_post_inner_url=URL('add_post_inner', signer=url_signer),
        files_info_url=URL('files_info', signer=url_signer),
        obtain_gcs_url=URL('obtain_gcs', signer=url_signer),
        notify_url=URL('notify_upload', signer=url_signer),
        delete_url=URL('notify_delete', signer=url_signer),
        get_posts_url=URL('get_posts', signer=url_signer),
        get_images_url=URL('get_images', signer=url_signer),
        get_image_url=URL('get_image', signer=url_signer),

    )

@action('addPostPg/<parent_post_id:int>')
@action.uses('addPostPg.html', db, auth, url_signer, auth.user)
def add_post(parent_post_id):
    # orphans = db(db.post.is_child == False).select().as_list()
    return dict(
        # orphans = orphans,
        parent_post_id = parent_post_id,
        add_post_inner_url=URL('add_post_inner', signer=url_signer),
        files_info_url=URL('files_info', signer=url_signer),
        obtain_gcs_url=URL('obtain_gcs', signer=url_signer),
        notify_url=URL('notify_upload', signer=url_signer),
        delete_url=URL('notify_delete', signer=url_signer),
        get_posts_url=URL('get_posts', signer=url_signer),
        get_images_url=URL('get_images', signer=url_signer),
        get_image_url=URL('get_image', signer=url_signer),
    )

@action('myPost')
@action.uses(db, auth, 'myPost.html',url_signer, auth.user)
def my_post():
    posts = db(db.post.owner == get_user_email()).select()
    images = db(db.image.owner == get_user_email()).select()
    return dict(posts=posts, images=images,
        add_post_inner_url=URL('add_post_inner', signer=url_signer),
        files_info_url=URL('files_info', signer=url_signer),
        obtain_gcs_url=URL('obtain_gcs', signer=url_signer),
        notify_url=URL('notify_upload', signer=url_signer),
        delete_url=URL('notify_delete', signer=url_signer),
        get_posts_url=URL('get_posts', signer=url_signer),
        )

@action('editPost/<post_id:int>', method=['GET', 'POST'])
@action.uses(db, session, auth.user, 'editPostPg.html')
def edit_post(post_id=None):
    assert post_id is not None
    p = db.post[post_id]
    if p is None:
        redirect(URL('myPost'))
    form = Form(db.post, record=p, deletable=False, csrf_session=session,
                formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('myPost'))
    return dict(form=form)

@action('deletePost/<post_id:int>')
@action.uses(db, session, auth, url_signer)
def delete(post_id=None):
    assert post_id is not None
    db(db.post.id == post_id).delete()
    redirect(URL('myPost'))
    
@action('add_post_inner',method=['GET', 'POST'])
@action.uses(url_signer.verify(), db)
def add_post_inner():
    rows = db(db.image).select().as_list()
    img_id = 0
    for row in rows:
        if row['owner'] == get_user_email():
            img_id = row['id']
    id = db.post.insert(
        title=request.json.get('title'),
        description= request.json.get('description'),
        image_id = img_id,
        parent_post=request.json.get('parent_id'),
    )
    return dict(id = id)


# -----------------Upload Cloud-----------------
    

#
# @action('index')
# @action.uses('index.html', url_signer, db, auth.user)
# def index():
#    return dict(
#        files_info_url = URL('files_info', signer=url_signer),
#        obtain_gcs_url = URL('obtain_gcs', signer=url_signer),
#        notify_url = URL('notify_upload', signer=url_signer),
#        delete_url = URL('notify_delete', signer=url_signer),
#    )

@action('files_info')
@action.uses(url_signer.verify(), db)
def files_info():
    """Returns to the web app the information about the file currently
    uploaded, if any, so that the user can download it or replace it with
    another file if desired."""
    rows = db(db.image).select().as_list()
    # The file is present if the row is not None, and if the upload was
    # confirmed.  Otherwise, the file has not been confirmed as uploaded,
    # and should be deleted.
    if rows is None:
        # There is no file.
        rows = {}
    for row in rows:
        row['data_url'] = ""
        row['id'] = row.get('id')
        row['file_path'] = row.get('file_path')
        row['file_name'] = row.get('file_name')
        row['file_type'] = row.get('file_type')
        row['file_date'] = row.get('file_date')
        row['file_size'] = row.get('file_size')
        row['download_url'] = None if row['file_path'] is None else gcs_url(GCS_KEYS, row['file_path'])
        row['upload_enabled'] = True
        row['download_enabled'] = True
    return dict(
        rows=rows
    )


@action('obtain_gcs', method="POST")
@action.uses(url_signer.verify(), db)
def obtain_gcs():
    """Returns the URL to do download / upload / delete for GCS."""
    verb = request.json.get("action")

    if verb == "PUT":
        mimetype = request.json.get("mimetype", "")
        file_name = request.json.get("file_name")
        extension = os.path.splitext(file_name)[1]
        # Use + and not join for Windows, thanks Blayke Larue
        file_path = BUCKET + "/" + str(uuid.uuid1()) + extension
        # Marks that the path may be used to upload a file.
        mark_possible_upload(file_path)
        upload_url = gcs_url(GCS_KEYS, file_path, verb='PUT',
                             content_type=mimetype)
        return dict(
            signed_url=upload_url,
            file_path=file_path
        )
    # look here later please
    elif verb in ["GET", "DELETE"]:
        file_path = request.json.get("file_path")
        if file_path is not None:
            # We check that the file_path belongs to the user.
            r = db(db.image.file_path == file_path).select().first()
            if r is not None:
                # Yes, we can let the deletion happen.
                signed_url = gcs_url(GCS_KEYS, file_path, verb=verb)
                return dict(signed_url=signed_url)
        # Otherwise, we return no URL, so we don't authorize the deletion.
        return dict(signer_url=None)


@action('notify_upload', method="POST")
@action.uses(url_signer.verify(), db)
def notify_upload():
    # I need to go back and change all get user_email with ids
    """We get the notification that the file has been uploaded."""
    file_type = request.json.get("file_type")
    file_name = request.json.get("file_name")
    file_path = request.json.get("file_path")
    file_size = request.json.get("file_size")
    d = datetime.datetime.utcnow()
    id = db.image.insert(
        owner=get_user_email(),
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        file_date=d,
        file_size=file_size,
        confirmed=True,
    )
    # Returns the file information.
    return dict(
        download_url=gcs_url(GCS_KEYS, file_path, verb='GET'),
        file_date=d,
        id = id,
    )


@action('notify_delete', method="POST")
@action.uses(url_signer.verify(), db)
def notify_delete():
    file_path = request.json.get("file_path")
    # We check that the owner matches to prevent DDOS.
    db((db.image.owner == get_user_email()) &
       (db.image.file_path == file_path)).delete()
    return dict()


def delete_path(file_path):
    """Deletes a file given the path, without giving error if the file
    is missing."""
    try:
        bucket, id = os.path.split(file_path)
        gcs.delete(bucket[1:], id)
    except:
        # Ignores errors due to missing file.
        pass
# change delete previous to delete single upload

 # destined to change


def mark_possible_upload(file_path):
    """Marks that a file might be uploaded next."""
    db.image.insert(
        owner=get_user_email(),
        file_path=file_path,
        confirmed=False,
    )

# profile

# load posts from database


@action('load_posts')
@action.uses(db, auth.user, url_signer)
def load_posts():
    rows = db(db.post.owner == get_user_email()).select().as_list()
    return dict(rows=rows)

# Get corresponding image from database


@action('get_image')
@action.uses(url_signer, db)
def get_image():
    post_id = int(request.params.get('row_id'))
    images = db((db.post.id == post_id)).select().first()
    image = db((db.image.id == images.image_id)).select().first()
    return dict(image=image)

# Profile Page


@action('profile/<email>')
@action.uses('profile.html', db, auth, session, url_signer)
def profile(email):
    # assert product_id is not None
    # Add after database stuff is done to check that profile exists
    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    if db(db.test).count() == 0:
        do_setup()
    
    print(email,"        dsfdsfdsfa\n\n\n")
    return dict(
        email = email,
        get_images_url=URL('get_images', signer=url_signer),
        get_image_url=URL('get_image', signer=url_signer),
        url_signer = url_signer,
        add_post_inner_url=URL('add_post_inner', signer=url_signer),
        files_info_url=URL('files_info', signer=url_signer),
        obtain_gcs_url=URL('obtain_gcs', signer=url_signer),
        notify_url=URL('notify_upload', signer=url_signer),
        delete_url=URL('notify_delete', signer=url_signer),
        get_posts_url=URL('get_posts', signer=url_signer),        
        )

@action('get_images')
@action.uses(url_signer.verify(), db)
def get_images():
    """Returns the lists of images."""
    images=db(db.test).select().as_list()
    
    in_progress_images=db((db.post.in_progress == True) & (db.post.owner == get_user_email())).select().as_list()
    
    finished_images=db((db.post.in_progress == False) & (db.post.owner == get_user_email())).select().as_list()

    return dict(images = images, in_progress_images = in_progress_images, finished_images = finished_images)


@action('get_posts')
@action.uses(url_signer.verify(), db)
def get_posts():
    """Returns to the web app the information about the file currently
    uploaded, if any, so that the user can download it or replace it with
    another file if desired."""
    posts = db(db.post).select().as_list()
    # print(posts)
    return dict(
        posts=posts
    )

@action('artwork/<post_id>')
@action.uses('artwork.html', db, auth, url_signer)
def artwork(post_id):
    return dict(
        # COMPLETE: return here any signed URLs you need.
        #my_callback_url = URL('my_callback', signer=url_signer),
        posts = db(db.post).select(),
        post_id = post_id,
        add_post_inner_url=URL('add_post_inner', signer=url_signer),
        files_info_url=URL('files_info', signer=url_signer),
        obtain_gcs_url=URL('obtain_gcs', signer=url_signer),
        notify_url=URL('notify_upload', signer=url_signer),
        delete_url=URL('notify_delete', signer=url_signer),
        get_posts_url=URL('get_posts', signer=url_signer),
        get_images_url=URL('get_images', signer=url_signer),
    )

