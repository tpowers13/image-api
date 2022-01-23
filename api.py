from flask import Flask, jsonify
from flask import request
from imagedb import Database
import requests
import uuid

app = Flask(__name__)
app.config['Content-Type'] = 'Content-Type'
db = Database()

auth = ''


@app.route('/images', methods=['GET'])
def get_images():
    q_params = None

    try:
        q_params = request.args.get('objects')
    except Exception as ex:
        print(ex)
        return 'Unable to get url parameters', 500

    # If no query parameters are present, then return all images
    try:
        if q_params is None:
            return jsonify(db.get_images(None)), 200
        else:
            lower_params = [obj.lower() for obj in q_params.split(',')]
            return jsonify(db.get_images(lower_params)), 200
    except Exception as ex:
        print(ex)
        return 'Unable to retrieve images from the database', 500


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        ret = db.get_image(image_id)
        if ret:
            return jsonify(ret), 200
        else:
            return "Image not found", 404
    except Exception as ex:
        print(ex)
        return 'Unable to retrieve image from the database', 500


@app.route('/images', methods=['POST'])
def add_image():
    data = request.get_json()

    # POST body validation
    if 'image' not in data:
        return 'Missing parameter image', 400
    if 'title' not in data:
        return 'Missing parameter data', 400
    if 'enabled' not in data:
        return 'Missing parameter enabled', 400
    if 'url' not in data:
        return 'Missing parameter url', 400
    if data['enabled'] is not '1' and data['enabled'] is not '0':
        return 'Invalid enabled flag', 400
    if data['image'] == "" and data['url'] == "":
        return 'Must provide image data or url', 400

    image = {
        'image': data['image'],
        'title': data['title'],
        'enabled': data['enabled'],
        'url': data['url'],
        'id': str(uuid.uuid4().hex),
        'objects': []
    }

    response = None
    if image['enabled'] == "1":
        try:
            # If a url is provided, then api call is simple
            if image['url']:
                response = requests.get(
                    'https://api.imagga.com/v2/tags?image_url=' + image['url'],
                    headers={
                        'Authorization': auth}
                )
            # If not, then upload the base64 encoded image, get the upload id, then get the objects (tags)
            else:
                response = requests.post(
                    'https://api.imagga.com/v2/uploads',
                    headers={
                        'Authorization': auth},
                    data={
                        'image_base64': image['image']
                    }
                )
                upload_id = response.json()['result']['upload_id']

                response = requests.get(
                    'https://api.imagga.com/v2/tags?image_upload_id=' + upload_id,
                    headers={
                        'Authorization': auth}
                )
            tags = response.json()['result']['tags']
            image['objects'] = [tag['tag']['en'] for tag in tags]
        except Exception as ex:
            print(ex)
            return 'Unable to call image service or parse response json', 500
    # Generate a title
    image['title'] = image['title'] if image['title'] else 'image_' + next(iter(image['objects']), '')
    try:
        db.add_image(image)
    except Exception as ex:
        print(ex)
        return 'Unable to add image to database', 500
    return image, 200


if __name__ == '__main__':
    app.run(port='5002')
