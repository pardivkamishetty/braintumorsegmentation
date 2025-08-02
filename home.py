import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import cv2
import base64
import json
import os

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
add_bg_from_local('image2.jpg')

# Function to load users from JSON file
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
    if username in users and users[username] == password:
        return True
    return False

# Function to handle user signup
def signup(users, username, password):
    if username in users:
        return False
    users[username] = password
    save_users(users)
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

# Main logic
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        # Display authentication form
        authentication()
    else:
        st.title(f"Welcome to the MRI scanner, {st.session_state['username']}!")
        
        # Main menu and navigation
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Upload Image", "Results","Logout"],
            icons=['house', 'cloud-upload', 'list-task'],
            orientation="horizontal",
        )
        if selected=="Logout":
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.experimental_rerun()

        # Home page
        if selected == "Home":
            st.title("HOME")
            add_bg_from_local('image8.jpg')  # Background image for home page
            st.title(':red[BRAIN TUMOR SEGMENTATION]')
            st.header("About BRAIN TUMOR")
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
            st.image(brain_image, caption='SIGNS OF BRAIN TUMOR', use_column_width=True)
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

        # Image uploader page
        elif selected == "Upload Image":
            st.title("Image Uploader")
            add_bg_from_local('image6.jpg')

            st.write("Upload an image for tumor detection.")
            
            uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file is not None:
                st.session_state.uploaded_image = Image.open(uploaded_file)
                st.success("Image uploaded successfully! Navigate to the 'Results' page to see the results.")

        # Results page
        elif selected == "Results":
            st.title("Results")
            
            if 'uploaded_image' not in st.session_state:
                st.warning("No image uploaded yet. Please upload an image from the 'Upload Image' page.")
            else:
                image = st.session_state.uploaded_image
                st.image(image, caption='Uploaded Image', use_column_width=True)
                
                # Perform tumor detection
                tumor_detected = detect_tumor(image)
                
                if tumor_detected:
                    st.error("Tumor detected in the image.")
                    
                    # Zoom into the image
                    width, height = image.size
                    left = width / 4
                    top = height / 4
                    right = 3 * width / 4
                    bottom = 3 * height / 4
                    zoomed_image = image.crop((left, top, right, bottom))
                    
                    st.image(zoomed_image, caption='Zoomed Image', use_column_width=True)
                else:
                    st.success("No tumor detected in the image.")

# Function to simulate tumor detection (replace with your actual model)
def detect_tumor(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    tumor_detected = np.any(thresholded)
    return tumor_detected

if __name__ == '__main__':
    main()
