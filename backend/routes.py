from linkedin import linkedin
from random import randint
from slugify import slugify
from cloudinary.uploader import upload
import base64
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, \
    jwt_required, jwt_refresh_token_required

from backend import app
from backend.models import WikiPage, PageEditLog, Member, Image
from backend.subroutines import linkedin_client, get_user_details


@app.route("/")
def initial_response():
    return jsonify("1")


@app.route("/check-token")
@jwt_required
def check_token():
    user_id = get_jwt_identity()
    return jsonify({})


@app.route("/page/<page_url>")
def load_page(page_url):
    page = WikiPage.query.filter(
        WikiPage.url == page_url
    ).first()

    images = []
    uploaded_images = Image.query.filter(Image.page_id == page.id)
    if uploaded_images.count() > 0:
        images = [row.to_dict()['image_url'] for row in uploaded_images]

    if not page:
        return jsonify({
            'error': "No such page"
        })

    return jsonify({
        'results': page.to_dict(),
        'images': images
    })


@app.route("/create", methods=["POST"])
@jwt_required
def create_page():
    user_id = get_jwt_identity()
    incoming = request.json
    title = incoming.get('title')
    content = incoming.get('body')

    url_slug = slugify(title)
    exists = WikiPage.query.filter(WikiPage.url == url_slug).first()
    if exists:
        for n in range(10):
            url_slug = slugify(title) + str(randint(0, 100))
            if not WikiPage.query.filter(WikiPage.url == url_slug).first():
                break

    WikiPage(
        title=title,
        page_content=content,
        url=url_slug,
        creator=user_id
    ).commit()

    return jsonify({
        'url': url_slug
    })


@app.route("/submit-edit", methods=["POST"])
@jwt_required
def submit_edit():
    user_id = get_jwt_identity()
    incoming = request.json
    edit = incoming.get('edit_text')
    url = incoming.get('purl')
    page = WikiPage.query.filter(
        WikiPage.url == url
    ).first()

    page.page_content = edit
    PageEditLog(
        editor=user_id,
        page_id=page.id
    ).commit()
    page.commit()

    return jsonify({
        'results': page.to_dict()
    })


@app.route("/all-pages")
def get_all_pages():
    pages = [row.to_dict() for row in WikiPage.query.filter()]
    return jsonify({
        'pages': pages
    })


@app.route("/login/linkedin/request")
def twitter_request_token():
    # request_origin = request.environ.get('HTTP_ORIGIN')
    client = linkedin_client()
    return jsonify({
        'redirect_url': client.authorization_url
    })


@app.route("/login/linkedin/confirm", methods=["POST"])
def twitter_confirm_token():
    code = request.json.get('code')
    client = linkedin_client()

    client.authorization_code = code
    access_token = client.get_access_token()
    user_client = linkedin.LinkedInApplication(token=access_token)
    first_name, last_name, email_address = get_user_details(user_client)

    existing_user = Member.query.filter(
        Member.email == email_address
    ).first()
    if not existing_user:
        existing_user = Member(
            first_name=first_name,
            last_name=last_name,
            email=email_address
        )
        existing_user.commit()

    access_token = create_access_token(identity=existing_user.id)
    refresh_token = create_refresh_token(identity=existing_user.id)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@app.route("/login/refresh")
@jwt_refresh_token_required
def refresh_token():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({
        'access_token': access_token
    })


@app.route("/image/upload", methods=["POST"])
@jwt_required
def upload_image():
    user_id = get_jwt_identity()
    incoming = request.json
    data = incoming.get('image_data')
    page_url = incoming.get('page_url')

    page = WikiPage.query.filter(WikiPage.url == page_url).first()

    data = data.split(",")
    image_header = data[0]
    image_data = data[1].encode('ascii')

    extension = image_header.replace("data:", "").replace(";base64", "").split("/")[1]
    file_name = f"/tmp/image-{uuid4().hex}.{extension}"
    with open(file_name, "wb") as fp:
        fp.write(base64.decodebytes(image_data))
        fp.close()

    url = upload(file_name)['url']
    Image(
        page_id=page.id,
        image_url=url
    ).commit()

    return jsonify({
        'url': url
    })
