from io import BytesIO
from PIL import Image
import pymongo
import bson
import streamlit as st
from datetime import datetime


def uploading(image, email):
    """
    Upload image to MongoDB with better error handling
    
    Args:
        image: PIL Image object
        email: User email for collection identification
        
    Returns:
        success: Boolean indicating upload success
        message: Success or error message
    """
    client = None
    
    try:
        # Validate inputs
        if not image:
            return False, "❌ No image provided"
        if not email:
            return False, "❌ No email provided"
            
        # Get image format
        image_format = image.format if image.format else 'PNG'

        # Convert the PIL Image to bytes
        byte_io = BytesIO()
        image.save(byte_io, format=image_format)
        image_bytes = byte_io.getvalue()

        # Validate image size (limit to 16MB for MongoDB)
        if len(image_bytes) > 16 * 1024 * 1024:  # 16MB limit
            return False, "❌ Image too large (max 16MB)"

        # Serialize the image bytes using BSON
        serialized_image = bson.Binary(image_bytes)

        # Connect to MongoDB and store the serialized image along with its format
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]

        # Create document with metadata
        document = {
            'image': serialized_image,
            'format': image_format,
            'upload_date': datetime.now(),
            'size_bytes': len(image_bytes),
            'image_mode': image.mode,
            'image_size': image.size
        }
        
        # Insert the document
        result = collection.insert_one(document)
        
        if result.inserted_id:
            return True, f"✅ Image uploaded successfully! ID: {str(result.inserted_id)[:8]}..."
        else:
            return False, "❌ Failed to insert image into database"
            
    except pymongo.errors.ConnectionFailure:
        return False, "❌ Could not connect to MongoDB. Please ensure MongoDB is running."
    except Exception as e:
        return False, f"❌ Upload error: {str(e)}"
    finally:
        # Always close the connection
        if client:
            client.close()


def delete_user_image(email, document_id):
    """
    Delete a specific image for a user
    
    Args:
        email: User email
        document_id: MongoDB document ID to delete
        
    Returns:
        success: Boolean indicating deletion success
        message: Success or error message
    """
    client = None
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]
        
        # Convert string ID to ObjectId
        from bson import ObjectId
        obj_id = ObjectId(document_id)
        
        # Delete the document
        result = collection.delete_one({'_id': obj_id})
        
        if result.deleted_count > 0:
            return True, "✅ Image deleted successfully"
        else:
            return False, "❌ Image not found"
            
    except pymongo.errors.ConnectionFailure:
        return False, "❌ Could not connect to MongoDB"
    except Exception as e:
        return False, f"❌ Deletion error: {str(e)}"
    finally:
        if client:
            client.close()


def clear_user_images(email):
    """
    Clear all images for a specific user
    
    Args:
        email: User email
        
    Returns:
        success: Boolean indicating success
        message: Success or error message
    """
    client = None
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Brain']
        collection = db[email]
        
        # Delete all documents for this user
        result = collection.delete_many({})
        
        if result.deleted_count > 0:
            return True, f"✅ Deleted {result.deleted_count} images"
        else:
            return True, "ℹ️ No images to delete"
            
    except pymongo.errors.ConnectionFailure:
        return False, "❌ Could not connect to MongoDB"
    except Exception as e:
        return False, f"❌ Clear error: {str(e)}"
    finally:
        if client:
            client.close()


def get_database_status():
    """
    Check MongoDB connection status
    
    Returns:
        status: Dictionary with connection info
    """
    client = None
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        
        # Test the connection
        client.admin.command('ismaster')
        
        # Get database info
        db = client['Brain']
        collections = db.list_collection_names()
        
        return {
            'connected': True,
            'message': '✅ MongoDB connected',
            'collections': len(collections),
            'database': 'Brain'
        }
        
    except pymongo.errors.ConnectionFailure:
        return {
            'connected': False,
            'message': '❌ MongoDB connection failed',
            'error': 'Connection timeout'
        }
    except Exception as e:
        return {
            'connected': False,
            'message': '❌ Database error',
            'error': str(e)
        }
    finally:
        if client:
            client.close()


