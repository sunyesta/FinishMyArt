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

# Temp tables for testing
TESTDATA = ["happy_star.svg", "cat.jpg", "tokage.png"]

url_signer = URLSigner(session)

def do_setup():
    db(db.test).delete()
    for img in TESTDATA:
        db.images.insert(image_url=URL('static', 'assets/' + img))


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
@action.uses() # Add here things you might want to use.
def file_upload():
    file_name = request.params.get("file_name")
    file_type = request.params.get("file_type")
    uploaded_file = request.body # This is a file, you can read it.
    # Diagnostics
    print("Uploaded", file_name, "of type", file_type)
    print("Content:", uploaded_file.read())
    return "ok"
