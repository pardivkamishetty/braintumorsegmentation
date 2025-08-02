import streamlit as st
from io import BytesIO
from PIL import Image
import pymongo


def image_ret(email):
    """
    Retrieve images from MongoDB for a specific user email
    
    Args:
        email: User email to retrieve images for
        
    Returns:
        images: List of PIL Image objects
    """
    images = []
    client = None
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]
        
        # Find all documents for this user
        documents = collection.find()
        
        for doc in documents:
            try:
                # Extract image bytes from document
                image_bytes = doc['image']
                
                # Convert bytes to PIL Image
                image = Image.open(BytesIO(image_bytes))
                images.append(image)
                
            except KeyError:
                st.warning(f"Document missing 'image' field: {doc.get('_id', 'unknown')}")
                continue
            except Exception as img_error:
                st.error(f"Error processing image: {str(img_error)}")
                continue
                
    except pymongo.errors.ConnectionFailure:
        st.error("❌ Could not connect to MongoDB. Please ensure MongoDB is running.")
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
    finally:
        # Always close the connection
        if client:
            client.close()
    
    return images


def image_ret_with_metadata(email):
    """
    Retrieve images with metadata from MongoDB for a specific user email
    
    Args:
        email: User email to retrieve images for
        
    Returns:
        results: List of dictionaries containing image and metadata
    """
    results = []
    client = None
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]
        
        # Find all documents for this user
        documents = collection.find()
        
        for doc in documents:
            try:
                # Extract image bytes and metadata
                image_bytes = doc['image']
                image_format = doc.get('format', 'Unknown')
                upload_date = doc.get('_id').generation_time if hasattr(doc.get('_id'), 'generation_time') else None
                
                # Convert bytes to PIL Image
                image = Image.open(BytesIO(image_bytes))
                
                # Create result object
                result = {
                    'image': image,
                    'format': image_format,
                    'upload_date': upload_date,
                    'document_id': str(doc['_id'])
                }
                
                results.append(result)
                
            except KeyError as key_error:
                st.warning(f"Document missing required field: {str(key_error)}")
                continue
            except Exception as img_error:
                st.error(f"Error processing image: {str(img_error)}")
                continue
                
    except pymongo.errors.ConnectionFailure:
        st.error("❌ Could not connect to MongoDB. Please ensure MongoDB is running.")
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
    finally:
        # Always close the connection
        if client:
            client.close()
    
    return results


def get_user_image_count(email):
    """
    Get the count of images for a specific user
    
    Args:
        email: User email to count images for
        
    Returns:
        count: Number of images for the user
    """
    client = None
    count = 0
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]
        
        # Count documents
        count = collection.count_documents({})
        
    except pymongo.errors.ConnectionFailure:
        st.error("❌ Could not connect to MongoDB. Please ensure MongoDB is running.")
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
    finally:
        # Always close the connection
        if client:
            client.close()
    
    return count