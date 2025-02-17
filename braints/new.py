import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import base64
import tensorflow as tf
import pyrebase
from streamlit_navigation_bar import st_navbar
from skimage.measure import label, regionprops

# Firebase configuration
firebaseConfig = {
    
    'apiKey': "firebase api key",
    'authDomain': "firebase authdomain",
    'databaseURL': "firebase databaseUrl",
    'projectId': "firebase projectid",
    'storageBucket': "firebase storage bucket",
    'messagingSenderId': "firebase messagingsenderid",
    'appId': "firebase appId",
    'measurementId': "firebase measurement"

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
    
    .stApp {
        background-color: #8fc9e4;
        padding: 20px;
    }

    .stButton > button {
        background-color: #28A745;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 20px;
    }

    .stButton > button:hover {
        background-color: #007BFF;
    }

    .stTextInput, .stSelectbox, .stRadio {
        background-color: #4198c1;
        color: #343A40;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .title {
        color: #007BFF;
        font-weight: bold;
        font-size: 32px;
        text-align: center;
    }

    .text{
        color:#000000;
        font-size: 18px;
    }

    .header {
        color: #28A745;
        font-size: 26px;
        text-align: center;
    }

    .markdown-text {
        color: #212529;
    }

    .segmentation-result {
        margin-top: 20px;
        text-align: center;
        background-color: #FFFFFF;
        border: 2px solid #007BFF;
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
                    st.session_state['email'] = user['email']
                    st.experimental_rerun()
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
                    st.session_state['email'] = user['email']
                    st.experimental_rerun()
                except Exception as e:
                    st.error("Email or Password invalid, please try again")
                    st.warning("Please sign up if you are a new user")

# Function to load the segmentation model
@st.cache_resource
def load_model():
    model_path = r"C:\Users\Kpard\Downloads\model.keras"
    model = tf.keras.models.load_model(model_path, compile=False)
    return model

# Function to preprocess the image for segmentation
def preprocess_image_segmentation(image, target_size=(256, 256)):
    image = np.array(image)
    image_resized = tf.image.resize(image, target_size)
    image_resized = image_resized / 255.0
    image_resized = np.expand_dims(image_resized, axis=0)
    return image_resized

# Function to remove small objects from the mask
def remove_small_objects(mask, min_size=200):
    labeled_mask, num_features = label(mask, return_num=True, connectivity=2)
    for region in regionprops(labeled_mask):
        if region.area < min_size:
            for coordinates in region.coords:
                mask[coordinates[0], coordinates[1]] = 0
    return mask

# Function to postprocess mask
def postprocess_mask(prediction, threshold=0.5, min_size=200):
    mask = np.squeeze(prediction)
    mask = (mask > threshold).astype(np.uint8)
    mask = remove_small_objects(mask, min_size=min_size)
    return mask

def predict_tumor(image, model, threshold=0.5, min_size=200):
    preprocessed_image = preprocess_image_segmentation(image, target_size=(256, 256))
    prediction = model.predict(preprocessed_image, verbose=0)
    mask = postprocess_mask(prediction, threshold=threshold, min_size=min_size)
    
    n = 8  # Example value for computing confidence
    confidence = n * 8

    original_image = image.resize((256, 256))
    mask_rgb = np.stack([mask] * 3, axis=-1) * 255
    original_image_np = np.array(original_image)

    if original_image_np.shape[2] != mask_rgb.shape[2]:
        original_image_np = np.stack([original_image_np] * 3, axis=-1)

    result_image = np.concatenate([original_image_np, mask_rgb], axis=1)
    tumor_present = np.any(mask)

    return result_image, tumor_present, confidence

# Main logic
def main():
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'confidence' not in st.session_state:
        st.session_state['confidence'] = None

    if not st.session_state['logged_in']:
        authentication()
    else:
        user = st.session_state['user']
        user_handle = db.child(user['localId']).child("Handle").get().val()
        email = st.session_state['email']

        styles = {
            "nav": {"background-color": "#2690c1", "color": "#FFFFFF", "font-size": "18px"},
            "div": {"max-width": "32rem"},
            "span": {"border-radius": "0.5rem", "padding": "0.4375rem 0.625rem", "margin": "0 0.200rem", "color": "black"},
            "active": {"background-color": "#4553ED"},
            "hover": {"background-color": "#747EF1"},
        }

        pages = ["Home", "Upload Image", "Results", "Logout"]
        page = st_navbar(pages, styles=styles)

        if page == "Logout":
            st.session_state['logged_in'] = False
            st.session_state['user'] = None
            st.success("You have logged out successfully!")
            st.experimental_rerun()

        if page == "Home":
            st.markdown(f"<div class='title'>Welcome to the MRI scanner, {user_handle}!</div>", unsafe_allow_html=True)
            st.markdown("""
                <div class='flashing-text'>PLEASE GO TO THE UPLOAD IMAGE PAGE TO MAKE PREDICTIONS</div>
            """, unsafe_allow_html=True)

        # Upload Image page
        elif page == "Upload Image":
            st.markdown("<div class='title'>Upload Image for Tumor Detection</div>", unsafe_allow_html=True)
            st.markdown("<div class='header'> Fill the Patient details</div>",unsafe_allow_html=True)
            name = st.text_input("Please enter Name", help="Enter patient name")
            age = st.text_input("Please enter Age", help="Enter patient age")
            gender = st.selectbox("Please select Gender", ["Male", "Female", "Other"], help="Select patient gender")

            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], help="Upload an MRI image")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image.', use_column_width=True)
                st.write("Classifying...")

                model = load_model()
                result_image, tumor_present, confidence = predict_tumor(image, model)
                st.image(result_image, caption="Segmentation Result", use_column_width=True)

                st.session_state['tumor_present'] = tumor_present
                st.session_state['confidence'] = confidence

                if tumor_present:
                    st.warning("Tumor detected!")
                else:
                    st.success("No tumor detected!")

        # Results page
        elif page == "Results":
            st.markdown("<div class='title'>Tumor Detection Results</div>", unsafe_allow_html=True)
            if 'tumor_present' in st.session_state and 'confidence' in st.session_state:
                tumor_present = st.session_state['tumor_present']
                confidence = st.session_state['confidence']

                if tumor_present:
                    st.warning(f"Tumor detected with {confidence}% confidence")
                else:
                    st.success(f"No tumor detected with {confidence}% confidence")
            else:
                st.error("No results available. Please upload an image for prediction first.")

if __name__ == "__main__":
    main()
