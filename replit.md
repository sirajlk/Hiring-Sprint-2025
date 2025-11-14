# Car Damage Detection

## Overview
This is an AI-powered YOLOv8-based car damage detection system that uses computer vision to identify and visualize damaged parts in car images. The application features a modern FastAPI backend with a pre-trained ONNX model and a beautiful, responsive web interface.

## Project Structure
- `my_fastapi_app/` - Main application directory
  - `main.py` - FastAPI application with enhanced web interface and detection API
  - `best.onnx` - Pre-trained YOLOv8 model (12MB)
  - `app.py` - Legacy Streamlit app (not currently used)
- `data/` - Training data and test images
- `runs/` - Model training runs and results
- `requirements.txt` - Python dependencies (FastAPI, uvicorn, opencv-python, numpy, Pillow)

## Technology Stack
- **Backend**: FastAPI with CORS middleware
- **ML Framework**: OpenCV DNN module
- **Model**: YOLOv8 (ONNX format)
- **Server**: Uvicorn (production-ready)
- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design

## Features
- **Visual Damage Detection**: Draws color-coded bounding boxes around detected damage with confidence labels
- **Dual Image Display**: Shows original and annotated images side-by-side
- **Modern UI**: Beautiful gradient design with drag-and-drop file upload
- **Download Results**: Export annotated images with detected damage
- **Real-time Feedback**: Loading states, progress indicators, and error handling
- **Mobile Responsive**: Works seamlessly on desktop and mobile devices

## Detected Classes
The model can detect 8 types of car damage:
1. Damaged door
2. Damaged window
3. Damaged headlight
4. Damaged mirror
5. Dent
6. Damaged hood
7. Damaged bumper
8. Damaged windshield

## Configuration
- **Port**: 5000 (frontend)
- **Host**: 0.0.0.0
- **CORS**: Enabled for all origins
- **Model Path**: my_fastapi_app/best.onnx

## API Endpoints
- `GET /` - Modern web interface with drag-and-drop upload
- `POST /detection` - Enhanced damage detection API
  - Accepts: Image file (multipart/form-data)
  - Returns: JSON with:
    - `classes`: Array of detected damage types
    - `confidences`: Array of confidence scores (%)
    - `boxes`: Array of bounding box coordinates
    - `annotated_image`: Base64-encoded PNG with visual annotations

## Deployment
Configured for Replit's autoscale deployment:
- Stateless web application
- Automatically scales based on traffic
- Uses uvicorn for production serving
- Environment: Python 3.11

## Usage
1. Open the web interface at the application URL
2. Click "Choose Image" or drag & drop a car image
3. Click "Analyze Damage" to process the image
4. View results:
   - Original image on the left
   - Annotated image with bounding boxes on the right
   - Detection summary with confidence scores
5. Download the annotated image if needed

## Recent Changes
- 2024-11-14: Major UI/UX enhancement
  - Redesigned frontend with modern gradient theme
  - Added bounding box visualization with color-coded labels
  - Implemented side-by-side image comparison
  - Added drag-and-drop file upload
  - Included download button for annotated results
  - Enhanced error handling and loading states
  - Made interface fully responsive for mobile devices
  
- 2024-11-14: Initial setup for Replit environment
  - Configured FastAPI to run on port 5000
  - Added CORS middleware for web interface
  - Set up deployment configuration
  - Created Python environment with all dependencies
