import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import base64
import json
import os
import tensorflow as tf

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-color: #002b36;
    }
    .stButton > button {
        color: #fafafa;
        background-color: #d33682;
        border: None;
    }
    .stRadio > label {
        color: #fafafa;
    }
    .css-1d391kg {
        color: #fafafa;
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

# Function to load users from JSON file
@st.cache_data
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            users = json.load(file)
    else:
        users = {}
    return users

# Function to save users to JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Function to handle user login
def login(users, username, password):
    if username in users and users[username]['password'] == password:
        return True
    return False

# Function to handle user signup
def signup(users, username, password):
    if username in users:
        return False
    users[username] = {'password': password, 'images': []}
    save_users(users)
    os.makedirs(f"uploads/{username}", exist_ok=True)
    return True

# Authentication logic
def authentication():
    st.title("Login and Signup System")

    users = load_users()

    auth_choice = st.radio("Select", ["Login", "Signup"])

    if auth_choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if login(users, username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
    elif auth_choice == "Signup":
        st.subheader("Signup")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        if st.button("Signup"):
            if signup(users, new_username, new_password):
                st.success("Account created successfully")
                st.info("Please login")
            else:
                st.error("Username already taken")

# Function to load the model once
@st.cache_resource
def load_model():
    model_path = r"C:\Users\deshp\OneDrive\PYTHON\BrainTumour10Epochscategorical.h5"
    return tf.keras.models.load_model(model_path)

# Function to preprocess image for the model
def preprocess_image(image):
    img_array = np.array(image.resize((64, 64)))  # Resize image to the input size expected by the model
    img_array = img_array / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to get ground truth label
# Replace this with your actual logic to obtain ground truth
def get_ground_truth(image_path):
    # For demonstration, assume ground truth is "No Tumor"
    return 0  # 0 for "No Tumor", 1 for "Tumor"

# Function to calculate accuracy
def calculate_accuracy(predictions, ground_truth):
    predicted_class = np.argmax(predictions, axis=1)[0]
    return 1.0 if predicted_class == ground_truth else 0.0

# Function to resize image for display
def resize_image(image, size=(150, 150)):
    return image.resize(size)

# Main logic
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Check the logged_in state
    if not st.session_state['logged_in']:
        # Display authentication form
        authentication()
    else:
        #st.title(f"Welcome to the MRI scanner, {st.session_state['username']}!")
        
        # Main menu and navigation
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Upload Image", "Results", "Logout"],
            icons=['house', 'cloud-upload', 'list-task', 'box-arrow-right'],
            orientation="horizontal",
        )
        if selected == "Logout":
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.experimental_rerun()

        # Home page
        
        if selected == "Home":
            st.title(f"Welcome to the MRI scanner, {st.session_state['username']}!")
            st.title(':red[BRAIN TUMOR SEGMENTATION]')
            st.header("About BRAIN TUMOR")
            st.markdown("""
            A :red[*Brain Tumor*] is an abnormal growth of tissue in the brain that can form in any part of the brain.
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
            st.image(brain_image, caption='SIGNS OF BRAIN TUMOR', use_column_width=True)
            st.write("""
            A brain tumor is a growth of cells in the brain or near it. Brain tumors can happen in the brain tissue. Brain tumors also can happen near the brain tissue. 
            Nearby locations include nerves, the pituitary gland, the pineal gland, and the membranes that cover the surface of the brain.
            
            Brain tumors range in size from very small to very large. Some brain tumors are found when they are very small because they cause symptoms that you notice right away. Other brain tumors grow very large before they're found. Some parts of the brain are less active than others. If a brain tumor starts in a part of the brain that's less active, it might not cause symptoms right away. The brain tumor size could become quite large before the tumor is detected.
            Brain tumor treatment options depend on the type of brain tumor you have, as well as its size and location. Common treatments include surgery and radiation therapy.
            """)
            brain1_image = Image.open('image3.jpg')
            st.image(brain1_image)
            st.write("""
            There are many types of brain tumors. The type of brain tumor is based on the kind of cells that make up the tumor. Special lab tests on the tumor cells can give information about the cells. Your health care team uses this information to figure out the type of brain tumor.
            
            Some types of brain tumors usually aren't cancerous. These are called noncancerous brain tumors or benign brain tumors. Some types of brain tumors usually are cancerous. These types are called brain cancers or malignant brain tumors. Some brain tumor types can be benign or malignant.  
            
            Benign brain tumors tend to be slow-growing brain tumors. Malignant brain tumors tend to be fast-growing brain tumors.       
            """)

        # Image uploader page
        elif selected == "Upload Image":
            st.title("Image Uploader")
            st.write("Upload an image for tumor detection.")
            
            # Display previously uploaded images
            users = load_users()
            username = st.session_state['username']
            user_images = users[username]['images']
            
            if user_images:
                st.subheader("Previously Uploaded Images")
                cols = st.columns(4)  # Create columns for grid layout
                for i, image_path in enumerate(user_images):
                    with cols[i % 4]:
                        image = Image.open(image_path)
                        resized_image = resize_image(image)
                        st.image(resized_image, use_column_width=True, caption=os.path.basename(image_path))
            else:
                st.subheader("No previously uploaded images")

            uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file is not None:
                user_dir = f"uploads/{username}"
                os.makedirs(user_dir, exist_ok=True)
                
                file_path = os.path.join(user_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.session_state.uploaded_image = Image.open(file_path)
                st.session_state.uploaded_image_path = file_path

                users[username]['images'].append(file_path)
                save_users(users)

                st.success("Image uploaded successfully! Navigate to the 'Results' page to see the results.")

        # Results page
        elif selected == "Results":
            st.markdown(
                """
                <style>
                .stApp {
                    background-color:#002b36;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.title("Results")
            
            if 'uploaded_image' not in st.session_state:
                st.warning("No image uploaded yet. Please upload an image from the 'Upload Image' page.")
            else:
                image = st.session_state.uploaded_image
                image_path = st.session_state.uploaded_image_path
                
                st.image(image, caption='Uploaded Image', use_column_width=True)
                
                # Load model
                model = load_model()
                
                # Preprocess image
                processed_image = preprocess_image(image)
                
                # Get predictions
                predictions = model.predict(processed_image)
                confidence = np.max(predictions) * 100
                predicted_class = np.argmax(predictions, axis=1)[0]
                
                # Get ground truth
                ground_truth = get_ground_truth(image_path)
                
                # Calculate accuracy (for demonstration purposes, always 100%)
                
                
                # Display results
                if confidence==100:
                    st.write(f"Confidence Level: 99")
                else:
                    st.write(f"Confidence Level: {confidence:.2f}%")
                
                
                if predicted_class == 0:
                    st.write("Prediction: No Tumor")
                else:
                    st.write("Prediction: Tumor")

if __name__ == "__main__":
    main()