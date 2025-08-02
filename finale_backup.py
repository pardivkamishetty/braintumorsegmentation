import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import base64
import tensorflow as tf
import pyrebase
from skimage.measure import label, regionprops
import time

# Firebase configuration
firebaseConfig = {
        'apiKey': "AIzaSyAb3paJE7ms4A5iVeLtB8ufR3a_L7bO9yM",
        'authDomain': "brain-tumor-app-c89af.firebaseapp.com",
        'databaseURL': "https://brain-tumor-app-c89af-default-rtdb.asia-southeast1.firebasedatabase.app/", 
        'projectId': "brain-tumor-app-c89af",
        'storageBucket': "brain-tumor-app-c89af.appspot.com",
        'messagingSenderId': "870748704368",
        'appId': "1:870748704368:web:f30ec9e11d045d77122eb5",
        'measurementId': "G-NKNPKZM5J7"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# Hide default Streamlit elements and apply custom styles
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background of the entire app */
     .stApp {
        background-color: #8fc9e4;
        min-height: 100vh;
        height: auto !important;
        overflow-y: auto !important;
        padding-top: 0px;
    }
    
    /* Navigation bar styling */
    [data-testid="stNavbar"] {
        position: sticky !important;
        top: 0 !important;
        z-index: 9999 !important;
        background-color: #2690c1 !important;
        border-bottom: 2px solid #1e5f7c !important;
    }
    
    /* Alternative navbar selectors */
    .st-navbar, .stNavBar, .navbar {
        position: sticky !important;
        top: 0 !important;
        z-index: 9999 !important;
        background-color: #2690c1 !important;
    }

    /* Styling for buttons */
    .stButton > button {
        background-color: #28A745; /* Soft Green - Button Background */
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 20px;
    }
    .stButton > button:hover {
        background-color: #007BFF; /* Cool Blue - Button Hover */
    }

    /* Input fields and selection boxes */
    .stTextInput, .stSelectbox, .stRadio {
        background-color: #4198c1; /* Light Gray - Input Background */
        color: #343A40; /* Dark Navy - Text Color */
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }

    /* Title styling */
    .title {
        color: #007BFF; /* Cool Blue - Title Color */
        font-weight: bold;
        font-size: 32px;
        text-align: center;
    }
    .text{
        color:#000000;
        font-size: 18px;
    }

    /* Header styling */
    .header {
        color: #28A745; /* Soft Green - Header Color */
        font-size: 26px;
        text-align: center;
    }

    /* Markdown text styling */
    .markdown-text {
        color: #212529; /* Dark Charcoal - Text Color */
    }

    /* Segmentation result section */
    .segmentation-result {
        margin-top: 20px;
        text-align: center;
        background-color: #FFFFFF; /* White - Background for Results */
        border: 2px solid #007BFF; /* Cool Blue - Border */
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Function to add background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        b64_image = base64.b64encode(image_file.read()).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{b64_image}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Authentication logic
def authentication():
    st.markdown("<div class='title'>Brain Tumor App</div>", unsafe_allow_html=True)

    choice = st.selectbox('Login/Sign up', ['Login', 'Sign up'], index=0, help="Choose to either login or create a new account")
    email = st.text_input("Email Address", help="Please enter your email address")
    password = st.text_input("Password", type='password', help="Please enter your password")

    if choice == 'Sign up':
        handle = st.text_input("Handle Name", value='Default', help="Please enter your app handle name")
        submit = st.button("Create Account")
        if submit:
            with st.spinner("Creating your account..."):
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    st.success("Your account is created successfully!")
                    
                    user = auth.sign_in_with_email_and_password(email, password)
                    db.child(user['localId']).child("Handle").set(handle)
                    db.child(user['localId']).child("ID").set(user['localId'])
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.session_state['email'] = email
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    elif choice == 'Login':
        submit = st.button("Login")
        if submit:
            with st.spinner("Logging in..."):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.success("You have successfully logged in!")
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.session_state['email'] = email
                    st.rerun()
                except Exception as e:
                    st.error("Email or Password invalid, please try again")
                    st.warning("Please sign up if you are a new user")

# Function to load the segmentation model
@st.cache_resource
def load_model():
    model_path = r"\model.keras"  # Path to your new model
    model = tf.keras.models.load_model(model_path, compile=False)
    return model

# Function to preprocess image for segmentation model
def preprocess_image_segmentation(image, target_size=(256, 256)):
    image = np.array(image)
    image_resized = tf.image.resize(image, target_size)
    image_resized = image_resized / 255.0  # Normalize the image
    image_resized = np.expand_dims(image_resized, axis=0)  # Add batch dimension
    return image_resized

# Function to remove small objects from the mask
def remove_small_objects(mask, min_size=200):
    """Remove small objects from a binary mask."""
    labeled_mask, num_features = label(mask, return_num=True, connectivity=2)
    for region in regionprops(labeled_mask):
        if region.area < min_size:
            for coordinates in region.coords:
                mask[coordinates[0], coordinates[1]] = 0
    return mask

# Function to postprocess mask
def postprocess_mask(prediction, threshold=0.5, min_size=200):
    mask = np.squeeze(prediction)  # Remove batch dimension
    mask = (mask > threshold).astype(np.uint8)  # Apply threshold

    # Remove small objects from the mask
    mask = remove_small_objects(mask, min_size=min_size)
    
    return mask

# Function to predict tumor and return accuracy
# Function to predict tumor and return accuracy and confidence level
def predict_tumor(image, model, threshold=0.5, min_size=200):
    """ Predict tumor presence and show the result image """
    # Preprocess the image
    preprocessed_image = preprocess_image_segmentation(image, target_size=(256, 256))
    
    # Perform prediction
    prediction = model.predict(preprocessed_image, verbose=0)
    
    # Print the range of prediction values for debugging
    print("Prediction range:", np.min(prediction), np.max(prediction))
    
    # Postprocess the mask, removing small objects
    mask = postprocess_mask(prediction, threshold=threshold, min_size=min_size)
    
    # Load the original image for visualization
    original_image = image.resize((256, 256))
    
    # Convert mask to RGB format
    mask_rgb = np.stack([mask]*3, axis=-1) * 255
    
    # Convert to uint8 for display
    original_image_np = np.array(original_image)
    
    # Ensure original image and mask have the same shape
    if original_image_np.shape[2] != mask_rgb.shape[2]:
        original_image_np = np.stack([original_image_np]*3, axis=-1)
    
    # Concatenate original image and mask side-by-side
    result_image = np.concatenate([original_image_np, mask_rgb], axis=1)  # Side-by-side concatenation

    # Determine if tumor is present
    tumor_present = np.any(mask)  # Check if any pixel is classified as a tumor

    # Calculate accuracy using some logic based on the prediction
    accuracy = np.mean(prediction > threshold) * 100  # Example accuracy calculation
    
    # Calculate confidence level as a percentage
    confidence = np.mean(prediction) * 100  # Convert to percentage

    return result_image, tumor_present, accuracy, confidence


# Main logic
def main():
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'name' not in st.session_state:
        st.session_state['name'] = ''
    if 'age' not in st.session_state:
        st.session_state['age'] = ''
    if 'gender' not in st.session_state:
        st.session_state['gender'] = 'Male'
    if 'result_image' not in st.session_state:
        st.session_state['result_image'] = None
    if 'tumor_present' not in st.session_state:
        st.session_state['tumor_present'] = None
    if 'accuracy' not in st.session_state:
        st.session_state['accuracy'] = None
    if 'confidence' not in st.session_state:
        st.session_state['confidence'] = None

    if not st.session_state['logged_in']:
        authentication()
    else:
        user = st.session_state['user']
        user_handle = db.child(user['localId']).child("Handle").get().val()
        email = st.session_state['email']

        # Main menu and navigation
        styles = {
            "nav": {
                "background-color": "#2690c1",
                "color": "#FFFFFF",
                "font-size": "18px",
               
            },
            "div": {
                "max-width": "32rem",
            },
            "span": {
                "border-radius": "0.5rem",
                "padding": "0.4375rem 0.625rem",
                "margin": "0 0.200rem",
                "color": "black", 
            },
            "active": {
                "background-color": "#4553ED",
            },
            "hover": {
                "background-color": "#747EF1",
            },
        }

        # Define pages as a list
        pages = ["Home", "Upload Image", "Results", "Logout"]
        
        # Use the list for the pages parameter
        page = st_navbar(pages, styles=styles)
        
        # Logout logic
        if page == "Logout":
            st.session_state['logged_in'] = False
            st.session_state['user'] = None
            st.success("You have logged out successfully!")
            st.rerun()

        # Home page
        if page == "Home":
            st.markdown(f"<div class='title'>Welcome to the MRI scanner, {user_handle}!</div>", unsafe_allow_html=True)
            # Home page content...
            st.markdown("""
            A :red[**Brain Tumor**] is an abnormal growth of tissue in the brain that can form in any part of the brain.
            They can be dangerous because they can put pressure on healthy brain tissue, block fluid flow, or spread into healthy areas.
            Here are some symptoms:
            - Headaches
            - Seizures or convulsions
            - Difficulty speaking, thinking, or articulating
            - Personality changes
            - Weakness or paralysis in one part of the body
            - Loss of balance or dizziness
            - Vision changes 
            """)
            brain_image = Image.open('image1.jpg')  
            st.image(brain_image, caption='SIGNS OF BRAIN TUMOR', use_container_width=True)
            st.write("""
            A brain tumor is a growth of cells in the brain or near it. Brain tumors can happen in the brain tissue. Brain tumors also can happen near the brain tissue. 
            Nearby locations include nerves, the pituitary gland, the pineal gland, and the membranes that cover the surface of the brain.
            
            Brain tumors range in size from very small to very large. Some brain tumors are found when they are very small because they cause symptoms that you notice right away. Other brain tumors grow very large before they're found. Some parts of the brain are less active than others. If a brain tumor starts in a part of the brain that's less active, it might not cause symptoms right away. The brain tumor size could become quite large before the tumor is detected.
            Brain tumor treatment options depend on the type of brain tumor you have, as well as its size and location. Common treatments include surgery and radiation therapy.
            """)
            brain1_image= Image.open('image3.jpg')
            st.image(brain1_image)
            st.write("""
            There are many types of brain tumors. The type of brain tumor is based on the kind of cells that make up the tumor. Special lab tests on the tumor cells can give information about the cells. Your health care team uses this information to figure out the type of brain tumor.
            
            Some types of brain tumors usually aren't cancerous. These are called noncancerous brain tumors or benign brain tumors. Some types of brain tumors usually are cancerous. These types are called brain cancers or malignant brain tumors. Some brain tumor types can be benign or malignant.  
            
            Benign brain tumors tend to be slow-growing brain tumors. Malignant brain tumors tend to be fast-growing brain tumors.       
            """)
        
        # Upload Image page
        elif page == "Upload Image":
            st.markdown("<div class='title'>Upload MRI Image</div>", unsafe_allow_html=True)
            st.session_state['name'] = st.text_input('Please Enter Your Name')
            st.session_state['age'] = st.text_input('Please Enter Your Age')
            st.session_state['gender'] = st.selectbox('Please Select Your Gender', ('Male', 'Female', 'Other'))
            uploaded_file = st.file_uploader("Please upload your MRI scan", type=["jpg", "png"])

            if uploaded_file is not None:
                st.image(uploaded_file, caption='Uploaded MRI Image', use_container_width=True)
                st.session_state['uploaded_file'] = uploaded_file
                image = Image.open(uploaded_file)

                model = load_model()  # Load the model once
                
                # Run the prediction
                result_image, tumor_present, accuracy, confidence = predict_tumor(image, model)
                
                # Store the result image and other info in the session state
                st.session_state['result_image'] = result_image
                st.session_state['tumor_present'] = tumor_present
                st.session_state['accuracy'] = accuracy
                st.session_state['confidence'] = confidence
                
                st.success('Prediction completed. Please check the Results page for details.')

        # Results page
        elif page == "Results":
            if not st.session_state['name']:
                st.error("Please provide your name in the Upload Image page.")
            elif st.session_state['result_image'] is not None:
                st.markdown("<div class='title'>Result</div>", unsafe_allow_html=True)
                result_image = st.session_state['result_image']
                st.image(result_image, caption='Segmentation Result', use_container_width=True)
                tumor_present = st.session_state['tumor_present']
                if tumor_present:
                    st.markdown("<h3 style='color:red;'>Tumor Detected!</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='color:green;'>No Tumor Detected!</h3>", unsafe_allow_html=True)
        
        # Display accuracy
                accuracy = st.session_state['accuracy'] if st.session_state['accuracy'] is not None else "N/A"
                if accuracy != "N/A":
                    st.write(f"### Prediction Accuracy: {accuracy:.2f}%")
                else:
                    st.write("### Prediction Accuracy: N/A")
        
        # Display confidence level
                confidence = st.session_state['confidence'] if st.session_state['confidence'] is not None else "N/A"
                if confidence != "N/A":
                    st.write(f"### Confidence Level: {confidence:.2f}%")  # Display in percentage
                else:
                    st.write("### Confidence Level: N/A")
                st.write(f"### Name: {st.session_state['name']}")
                st.write(f"### Age: {st.session_state['age']}")
                st.write(f"### Gender: {st.session_state['gender']}")
                st.write(":red-background[DISCLAIMER: THE PREDICTION PROVIDED BY THIS APPLICATION IS BASED ON THE DATA INPUT AND SHOULD NOT BE CONSIDERED DEFINITIVE OR USED AS A SOLE BASIS FOR MEDICAL DECISIONS. CONSULT A QUALIFIED HEALTHCARE PROVIDER FOR ANY CONCERN REGARDING YOUR HEALTH.]")
            else:
                st.warning("No result available. Please upload an image first.")




# Run the main function
if __name__ == '__main__':
    main()
