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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

BUCKET = '/finishmyart-pictures '
# GCS keys.  You have to create them for this to work.  See README.md
GCS_KEY_PATH = os.path.join(APP_FOLDER, 'private/gcs_keys.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

# I create a handle to gcs, to perform the various operations.
gcs = NQGCS(json_key_path=GCS_KEY_PATH)



@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    user = auth.get_user()
    posts = db(db.post).select()
    return dict(posts=posts)
    


@action('landing')
@action.uses('landing.html', db, auth, url_signer)
def landing():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        #my_callback_url = URL('my_callback', signer=url_signer),
    )

@action('auth/upload')
@action.uses('upload.html', db, auth, url_signer)
def upload():
    return dict(file_upload_url = URL('file_upload', signer=url_signer))

@action('myPost')
@action.uses(db, auth.user, 'myPost.html')
def my_post():
    posts = db(db.post.created_by == get_user_email()).select()
    return dict(posts=posts)


@action('addPost', method=["GET", "POST"])
@action.uses(db, session,auth.user, 'addPost.html')
def add_post():
    form = Form(db.post, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('myPost'))
    return dict(form=form)

@action('editPost/<post_id:int>', method=['GET', 'POST'])
@action.uses(db, session, auth.user, 'editPost.html')
def edit_post(post_id):
    p = db.post[post_id]
    if not p:
        redirect(URL('myPost'))
    form = Form(db.post, record=p, csrf_session=session, formstyle=FormStyleBulma)
    return dict(form=form)

@action('artwork/<artwork_id>')
@action.uses('artwork.html', db, auth, url_signer)
def artwork(artwork_id):
    return dict(
        # COMPLETE: return here any signed URLs you need.
        #my_callback_url = URL('my_callback', signer=url_signer),
    )

#Profile Page
@action('profile')
@action.uses('profile.html', db, auth, session, url_signer)
def profile(product_id=None):
    #assert product_id is not None
    #Add after database stuff is done to check that profile exists
    return dict()

@action('file_upload', method="PUT")
@action.uses() 
def file_upload():
    file_name = request.params.get("file_name")
    file_type = request.params.get("file_type")
    uploaded_file = request.body 
    print("Uploaded", file_name, "of type", file_type)
    print("Content:", uploaded_file.read())
    return "ok"

##----------------------------------------------------------------------##
@action('file_info')
@action.uses(url_signer.verify(), db)
def file_info():
    row = db(db.upload.owner == get_user_email()).select().first()
    if row is not None and not row.confirmed:
        delete_path(row.file_path)
        row.delete_record()
        row = {}
    if row is None:
        row = {}
    file_path = row.get('file_path')
    return dict(
        file_name=row.get('file_name'),
        file_type=row.get('file_type'),
        file_date=row.get('file_date'),
        file_size=row.get('file_size'),
        file_path=file_path,
        download_url=None if file_path is None else gcs_url(GCS_KEYS, file_path),
        upload_enabled=True,
        download_enabled=True,
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
    elif verb in ["GET", "DELETE"]:
        file_path = request.json.get("file_path")
        if file_path is not None:
            # We check that the file_path belongs to the user.
            r = db(db.upload.file_path == file_path).select().first()
            if r is not None and r.owner == get_user_email():
                # Yes, we can let the deletion happen.
                delete_url = gcs_url(GCS_KEYS, file_path, verb='DELETE')
                return dict(signed_url=delete_url)
        # Otherwise, we return no URL, so we don't authorize the deletion.
        return dict(signer_url=None)

@action('notify_upload', method="POST")
@action.uses(url_signer.verify(), db)
def notify_upload():
    """We get the notification that the file has been uploaded."""
    file_type = request.json.get("file_type")
    file_name = request.json.get("file_name")
    file_path = request.json.get("file_path")
    file_size = request.json.get("file_size")
    # Deletes any previous file.
    rows = db(db.upload.owner == get_user_email()).select()
    for r in rows:
        if r.file_path != file_path:
            delete_path(r.file_path)
    # Marks the upload as confirmed.
    d = datetime.datetime.utcnow()
    db.upload.update_or_insert(
        ((db.upload.owner == get_user_email()) &
         (db.upload.file_path == file_path)),
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
    db((db.upload.owner == get_user_email()) &
       (db.upload.file_path == file_path)).delete()
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

def delete_previous_uploads():
    """Deletes all previous uploads for a user, to be ready to upload a new file."""
    previous = db(db.upload.owner == get_user_email()).select()
    for p in previous:
        # There should be only one, but let's delete them all.
        delete_path(p.file_path)
    db(db.upload.owner == get_user_email()).delete()

def mark_possible_upload(file_path):
    """Marks that a file might be uploaded next."""
    delete_previous_uploads()
    db.upload.insert(
        owner=get_user_email(),
        file_path=file_path,
        confirmed=False,
    )