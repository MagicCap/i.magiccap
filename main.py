from flask import Flask, redirect, send_file, request, jsonify
from models import InstallID
import requests
import boto3
import random
import string
import botocore
# Imports go here.

app = Flask(__name__)
# Defines the app.


@app.route("/")
def go_to_website():
    """Returns to magiccap.me"""
    return redirect("https://magiccap.me")


@app.route("/upload", methods=["POST"])
def upload():
    """Used to upload to i.magiccap"""
    try:
        auth_header = request.headers['Authorization']
    except KeyError:
        resp = jsonify({
            "error": "No authorization header present."
        })
        resp.status_code = 400
        return resp

    auth_header_split = auth_header.split(" ")
    if len(auth_header_split) != 2:
        resp = jsonify({
            "error": "Invalid authorization header present."
        })
        resp.status_code = 400
        return resp

    try:
        InstallID.get(auth_header_split[1])
    except InstallID.DoesNotExist:
        resp = jsonify({
            "error": "Invalid installation ID."
        })
        resp.status_code = 400
        return resp

    try:
        file = request.files['data']
    except KeyError:
        resp = jsonify({
            "error": "No data found."
        })
        resp.status_code = 400
        return resp

    filename = ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    ext = file.filename.split(".").pop().lower()

    boto3.resource("s3").Object("i.magiccap.me", f"{filename}.{ext}").put(Body=file, ContentType=file.content_type)

    return jsonify({
        "url": f"https://i.magiccap.me/{filename}.{ext}"
    })


@app.route("/<path:subpath>")
def image_view(subpath):
    """Loads a image view."""
    s3 = boto3.resource("s3")
    try:
        obj = s3.Object("i.magiccap.me", subpath)
        obj = obj.get()
    except botocore.exceptions.ClientError:
        r = requests.get(
            "https://hosting.novuscommunity.co/" + subpath,
            headers={
                "Host": "i.magiccap.me"
            },
            verify=False
        )
        
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            return "Not found.", 404

        obj.put(Body=r.content, ContentType=r.headers['Content-Type'])
        obj = s3.Object("i.magiccap.me", subpath).get()

    return send_file(obj['Body'], attachment_filename=subpath.split("/").pop(), mimetype=obj['ContentType'])


if __name__ == "__main__":
    app.run(port=7575, debug=True)
# Starts the app if this isn't a Lambda instance.
