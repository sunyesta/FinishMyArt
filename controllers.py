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
from nqgcs import NQGCS

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .settings import APP_FOLDER
from .gcs_url import gcs_url
from py4web.utils.form import Form, FormStyleBulma
from .common import Field
import datetime

# ---------Temp tables for testing--------
TESTDATA = ["happy_star.svg", "cat.jpg", "tokage.png"]

url_signer = URLSigner(session)

BUCKET = '/finishmyart-art'


GCS_KEY_PATH = os.path.join(APP_FOLDER, 'private/finishmyart-a7fc05f5fa13.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

# I create a handle to gcs, to perform the various operations.
gcs = NQGCS(json_key_path=GCS_KEY_PATH)


# -----------------Index-----------------


@action('vueTemp')
@action.uses('vueTemp.html', db, auth, url_signer)
def vueTemp():
    return dict()


@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    user = auth.get_user()
    posts = db(db.post).select()
    return dict(posts=posts)


# -----------------Upload-----------------
@action('auth/upload')
@action.uses('upload.html', db, auth, url_signer)
def upload():
    return dict(file_upload_url=URL('file_upload', signer=url_signer))


# -----------------myPost-----------------
@action('myPost')
@action.uses(db, auth.user, 'myPost.html')
def my_post():
    posts = db(db.post.owner == get_user_email()).select()
    images = db(db.image.owner == get_user_email()).select()
    return dict(posts=posts,
                images=images,
                load_posts_url = URL('load_posts', signer=url_signer),
                get_image_url = URL('get_image', signer=url_signer),
                )


@action('addPost', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'addPostPg.html')
def add_post():
    form = Form(
        [Field('title', length=100,),
        Field('description','text'),
        Field('is_child', 'boolean', default=False),
        Field('image', 'upload', uploadfolder='apps/FinishMyArt/static/art'),
        ],
        csrf_session=session, formstyle=FormStyleBulma)

    if form.accepted:
        databaseimageid = db.image.insert(
            image=form.vars['image'],
        )
        db.post.insert(
            title=form.vars['title'],
            description=form.vars['description'],
            is_child = form.vars['is_child'],
            image_id = databaseimageid,
        )
        redirect(URL('myPost'))
    return dict(form=form,
    )


@action('editPost/<post_id:int>', method=['GET', 'POST'])
@action.uses(db, session, auth.user, 'editPostPg.html')
def edit_post(post_id=None):
    assert post_id is not None
    p = db.post[post_id]
    if p is None:
        redirect(URL('myPost'))
    form = Form(db.post, record=p, csrf_session=session,
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


@action('artwork/<artwork_id>')
@action.uses('artwork.html', db, auth, url_signer)
def artwork(artwork_id):
    return dict(
        # COMPLETE: return here any signed URLs you need.
        # my_callback_url = URL('my_callback', signer=url_signer),
    )

#load posts from database
@action('load_posts')
@action.uses(db, auth.user, url_signer)
def load_posts():
    rows = db(db.post.owner == get_user_email()).select().as_list()
    return dict(rows=rows)

#Get corresponding image from database
@action('get_image')
@action.uses(url_signer, db)
def get_image():
    post_id = int(request.params.get('row_id'))
    images = db((db.post.id == post_id)).select().first()
    image = db((db.image.id == images.image_id)).select().first()
    return dict(image = image)

# Profile Page


@action('profile')
@action.uses('profile.html', db, auth, session, url_signer)
def profile():
    # assert product_id is not None
    # Add after database stuff is done to check that profile exists
    if db(db.test).count() == 0:
        do_setup()
    return dict(get_images_url = URL('get_images', signer=url_signer))


@action('file_upload', method="PUT")
@action.uses()
def file_upload():
    file_name = request.params.get("file_name")
    file_type = request.params.get("file_type")
    uploaded_file = request.body

    db.image.insert(
        image=uploaded_file,
        file_name=file_name,
        file_type=file_type,
    )

    db.post.insert(
        # title =
    )
    print("Uploaded", file_name, "of type", file_type)
    print("Content:", uploaded_file.read())
    return "ok"



# -----------------Upload Cloud-----------------


#
#@action('index')
#@action.uses('index.html', url_signer, db, auth.user)
#def index():
#    return dict(
#        file_info_url = URL('file_info', signer=url_signer),
#        obtain_gcs_url = URL('obtain_gcs', signer=url_signer),
#        notify_url = URL('notify_upload', signer=url_signer),
#        delete_url = URL('notify_delete', signer=url_signer),
#    )

@action('file_info')
@action.uses(url_signer.verify(), db)
def file_info():
    """Returns to the web app the information about the file currently
    uploaded, if any, so that the user can download it or replace it with
    another file if desired."""
    is_post = request.params.get('is_post')
    rows = db(db.image.is_post == is_post).select().list()
    # The file is present if the row is not None, and if the upload was
    # confirmed.  Otherwise, the file has not been confirmed as uploaded,
    # and should be deleted.
    if rows is None:
        # There is no file.
        rows = {}
    for row in rows:
        row['file_path'] = row.get('file_path')
        row['file_name'] = row.get('file_name')
        row['file_type'] = row.get('file_type')
        row['file_date'] = row.get('file_date')
        row['file_size'] = row.get('file_size')
        row['download_url'] = None if file_path is None else gcs_url(GCS_KEYS, file_path)
        row['upload_enabled'] = True
        row['download_enabled'] = True

    return dict(
        rows = rows
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
    #look here later please
    elif verb in ["GET", "DELETE"]:
        file_path = request.json.get("file_path")
        if file_path is not None:
            # We check that the file_path belongs to the user.
            r = db(db.upload.file_path == file_path).select().first()
            if r is not None and r.owner == get_user_email():
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
    db.upload.update_or_insert(
        ((db.image.owner == get_user_email()) &
         (db.image.file_path == file_path)),
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
#change delete previous to delete single upload

 #destined to change
def mark_possible_upload(file_path):
    """Marks that a file might be uploaded next."""
    db.upload.insert(
        owner=get_user_email(),
        file_path=file_path,
        confirmed=False,
    )
