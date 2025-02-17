from io import BytesIO
from PIL import Image
import pymongo
import bson

def uploading(image,email):
    image_format = image.format

    # Convert the PIL Image to bytes
    byte_io = BytesIO()
    image.save(byte_io, format=image_format)
    image_bytes = byte_io.getvalue()

    # Serialize the image bytes using BSON
    serialized_image = bson.Binary(image_bytes)

    # Connect to MongoDB and store the serialized image along with its format
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['Brain']

    collection = db[email]

    #collection = db['MRIscan']

    # Insert the serialized image into the collection
    document = {
        'image': serialized_image,
        'format': image_format
    }
    collection.insert_one(document)
    client.close()


