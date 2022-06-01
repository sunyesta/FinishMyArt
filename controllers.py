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
from .common import Field
import datetime

# ---------Temp tables for testing--------
TESTDATA = ["happy_star.svg", "cat.jpg", "tokage.png"]

url_signer = URLSigner(session)


def do_setup():
    db(db.test).delete()
    for img in TESTDATA:
        db.test.insert(image_url=URL('static', 'assets/' + img),
                       description="hello")


@action('get_images')
@action.uses(url_signer.verify(), db)
def get_images():
    """Returns the list of images."""
    return dict(images=db(db.test).select().as_list())

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
                images=images,)


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
        db.post.insert(
            title=form.vars['title'],
            description=form.vars['description'],
            is_child = form.vars['is_child'],
        )
        db.image.insert(
            image=form.vars['image'],
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

# Profile Page


@action('profile')
@action.uses('profile.html', db, auth, session, url_signer)
def profile():
    # assert product_id is not None
    # Add after database stuff is done to check that profile exists
    if db(db.test).count() == 0:
        do_setup()
    return dict(get_images_url=URL('get_images', signer=url_signer))


@action('file_upload', method="PUT")
@action.uses()
def file_upload():
    file_name = request.params.get("file_name")
    file_type = request.params.get("file_type")
    title = request.params.get("title")
    # description = request.params.get("description")
    # is_child = request.params.get("is_child")
    # parent_post = request.params.get("parent_post")
    # image_id = request.params.get("image_id")

    # uploaded_file = request.body

    # db.image.insert(
    #     image=uploaded_file,
    #     file_name=file_name,
    #     file_type=file_type,

    # )

    # db.post.insert(
    #     title=title
    #     description=description
    #     is_child=is_child,
    #     image_id=image_id,

    # )

    print("Uploaded", file_name, "of type", file_type)
    print("Content:", uploaded_file.read())
    return "ok"
