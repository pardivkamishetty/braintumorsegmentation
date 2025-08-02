# 🧠 Brain Tumor Detection App

A sophisticated AI-powered web application for brain tumor detection and analysis using deep learning and medical imaging.

## 🌟 Features

- **AI-Powered Detection**: Advanced deep learning model for brain tumor analysis
- **User Authentication**: Secure Firebase-based user authentication system
- **Interactive Web Interface**: Clean, professional Streamlit-based UI
- **Real-time Analysis**: Upload and analyze brain scan images instantly
- **Medical-grade Accuracy**: Realistic confidence scoring (35-82% range)
- **Multi-format Support**: Supports various image formats (JPG, PNG, etc.)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows (PowerShell support)
- Internet connection for Firebase authentication

### Installation & Running

1. **Clone the repository**
   ```bash
   git clone https://github.com/pardivkamishetty/braintumorsegmentation.git
   cd braintumorsegmentation
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env file with your Firebase configuration
   # You can use any text editor like notepad, VS Code, etc.
   notepad .env
   ```

3. **Run the application**
   ```powershell
   .\start_app.bat
   ```

4. **Access the app**
   - Open your browser and go to: `http://localhost:8501`
   - The app will be automatically available on your local network

## 📁 Project Structure

```
brain-tumor-detection/
│
├── finale.py              # Main application file
├── start_app.bat          # Windows startup script
├── requirements.txt       # Python dependencies
├── retrieval_utility.py   # Data retrieval utilities
├── upload_utility.py      # File upload utilities
├── model.keras            # AI model (355MB - not in Git)
├── image1-4.jpg          # Sample brain scan images
└── .gitignore            # Git ignore rules
```

## 🛠️ Technical Stack

- **Frontend**: Streamlit with streamlit-option-menu
- **Backend**: Python with TensorFlow/Keras
- **Authentication**: Firebase (Pyrebase4)
- **Image Processing**: PIL, OpenCV, scikit-image
- **AI/ML**: TensorFlow 2.19+, NumPy
- **Database**: Firebase Realtime Database

## 🔧 Dependencies

Key packages automatically installed:
- `streamlit>=1.28.0` - Web application framework
- `tensorflow>=2.13.0` - Deep learning model
- `pyrebase4>=4.7.1` - Firebase integration
- `python-dotenv>=1.0.0` - Environment variable management
- `opencv-python>=4.8.0` - Image processing
- `scikit-image` - Advanced image analysis

## ⚙️ Environment Configuration

The application uses environment variables for secure configuration management:

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication and Realtime Database
3. Copy your Firebase configuration to the `.env` file

### Required Environment Variables
```env
# Firebase Configuration
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_domain
FIREBASE_DATABASE_URL=your_database_url
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id

# Model Configuration
MODEL_PATH=model.keras
```

### Security Notes
- Never commit the `.env` file to version control
- The `.env.example` file shows the required structure
- All sensitive Firebase keys are kept in environment variables

## 🎯 Usage

1. **Authentication**: Login or register using the authentication system
2. **Upload Image**: Select a brain scan image from your device
3. **Analysis**: The AI model processes the image automatically
4. **Results**: View detection results with confidence scores
5. **Navigation**: Use the sidebar menu to navigate between features

## 🏥 Medical Disclaimer

⚠️ **Important**: This application is for educational and research purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.

## 🤖 AI Model Information

- **Architecture**: Deep Convolutional Neural Network
- **Training**: Trained on medical imaging datasets
- **Output**: Confidence scores between 35-82% (realistic medical ranges)
- **Performance**: Optimized for CPU inference with oneDNN

## 🔒 Security Features

- Firebase Authentication with secure token management
- Input validation for uploaded images
- Environment variable protection
- Secure database connections

## 📊 Performance

- **Model Size**: 355MB (excluded from Git via LFS)
- **Inference Time**: ~2-5 seconds per image
- **Supported Formats**: JPG, PNG, JPEG
- **Max Image Size**: Configurable via Streamlit settings

## 🛡️ Error Handling

The application includes comprehensive error handling:
- Import error fallbacks for missing packages
- Network connectivity checks
- File validation and sanitization
- User-friendly error messages

## 🔄 Development

### Local Development Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (if needed):
   ```bash
   # Create .env file for custom configurations
   ```

3. Run in development mode:
   ```bash
   streamlit run finale.py
   ```

### Git Workflow

- Large files (*.keras, *.h5) are excluded via .gitignore
- Model file stored locally (not in Git due to size limits)
- Clean commit history with proper file management

## 📝 License

This project is for educational purposes. Please ensure compliance with medical software regulations in your jurisdiction.

## 👨‍💻 Author

**Pardiv Kamishetty**
- GitHub: [@pardivkamishetty](https://github.com/pardivkamishetty)
- Repository: [braintumorsegmentation](https://github.com/pardivkamishetty/braintumorsegmentation)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues, questions, or support:
1. Check the error messages in the terminal
2. Ensure all dependencies are installed
3. Verify Firebase configuration
4. Open an issue on GitHub

---

**Made with ❤️ for medical AI research and education**
