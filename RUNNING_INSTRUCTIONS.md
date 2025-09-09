# Running the AI-HR System

## Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- pip (Python package manager)
- npm (Node package manager)

## Running the System

### Option 1: Run Backend and Frontend Separately

#### Backend
1. Navigate to the backend directory:
   ```
   cd ai-hr-hackaton/backend/api
   ```
2. Run the backend server:
   ```
   python main_optimized.py
   ```
3. The backend will be available at: http://127.0.0.1:8000
4. API documentation: http://127.0.0.1:8000/docs

#### Frontend
1. Navigate to the frontend directory:
   ```
   cd ai-hr-hackaton/frontend
   ```
2. Install dependencies (if not already installed):
   ```
   npm install
   ```
3. Run the frontend:
   ```
   npm start
   ```
4. The frontend will be available at: http://localhost:3000

### Option 2: Run Both Services with Batch Scripts

#### Using Individual Scripts
1. Run the backend:
   ```
   ai-hr-hackaton/backend/api/start_server_fixed.bat
   ```
2. Run the frontend:
   ```
   ai-hr-hackaton/frontend/start_fast_fixed.bat
   ```

#### Using Combined Script
1. Run both services together:
   ```
   ai-hr-hackaton/start_all.bat
   ```

## Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- Backend API Documentation: http://127.0.0.1:8000/docs

## Troubleshooting
1. If you encounter path issues, make sure you're running the scripts from the correct directory
2. If ports are already in use, you may need to stop existing processes:
   - Backend: `taskkill /f /im python.exe`
   - Frontend: `taskkill /f /im node.exe`
3. If dependencies are missing, install them:
   - Backend: `pip install -r requirements.txt` (in backend directory)
   - Frontend: `npm install` (in frontend directory)
