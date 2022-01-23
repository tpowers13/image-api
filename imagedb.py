import os
from flask import json

class Database:

    def __init__(self):
        self.image_json = os.getcwd() + '\\images.json'

    def get_images(self, object_search):
        with open(self.image_json, "r") as image_json_file:
            data = json.load(image_json_file)

        if object_search is None:
            return data['images']
        else:
            search = []
            for image in data['images']:
                if any(obj in object_search for obj in image['objects']):
                    search.append(image)
            return search

    def get_image(self, image_id):
        with open(self.image_json, "r") as image_json_file:
            data = json.load(image_json_file)
        return [d for d in data['images'] if d["id"]==str(image_id)]

    def add_image(self, image):
        with open(self.image_json, "r") as image_json_file:
            data = json.load(image_json_file)

        data['images'].append(image)

        with open(self.image_json, "w") as image_json_file:
            json.dump(data, image_json_file)
