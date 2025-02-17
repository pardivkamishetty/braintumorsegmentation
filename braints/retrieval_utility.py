import streamlit as st
from io import BytesIO
from PIL import Image
import pymongo


def image_ret(email):

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['Brain']
    collection = db[email]
    

    documents = collection.find()
    
    images = []
    
    for doc in documents:
        image_bytes = doc['image']
        image = Image.open(BytesIO(image_bytes))
        images.append(image)

    #st.write(images)
    client.close()
    
    return images