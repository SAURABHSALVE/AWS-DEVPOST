# Testing Guide: Backend + Frontend Integration

This guide shows you how to test both Task 1 (Backend) and Task 2 (Frontend) together.

## Prerequisites

- Python 3.8+ installed
- Both Backend and Frontend directories set up

## Step 1: Start the Backend Server

1. **Open Terminal/Command Prompt #1** and navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. **Activate the virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Start the Flask backend:**
   ```bash
   python app.py
   ```

   You should see output like:
   ```
   Starting Flask app on http://localhost:8080
   Available endpoints:
     Root: http://localhost:8080/
     Health: http://localhost:8080/health
     Ready: http://localhost:8080/ready
     API Status: http://localhost:8080/api/status
   ```

## Step 2: Start the Frontend Server

1. **Open Terminal/Command Prompt #2** and navigate to the Frontend directory:
   ```bash
   cd Frontend
   ```

2. **Start the frontend server:**
   ```bash
   python serve.py
   ```

   You should see output like:
   ```
   🚀 Frontend server starting...
   📱 Frontend URL: http://localhost:3000
   🔗 Test Connection: http://localhost:3000/test-connection.html
   🏠 Home Page: http://localhost:3000/index.html
   ```

## Step 3: Test the Integration

### Option A: Quick Start (Windows)

1. **Double-click `start-servers.bat`** - This will automatically:
   - Start the backend server
   - Start the frontend server  
   - Open the application in your browser

### Option B: Connection Test

1. **Open your browser** and go to: http://localhost:3000/simple-test.html

2. **The page will automatically test `/health`** and show results

3. **Use the test buttons** to manually test:
   - "Test /health" - Basic health check
   - "Test /ready" - Readiness check
   - "Test /api/status" - API status check

### Option B: Manual Testing

1. **Test Backend Directly:**
   ```bash
   # Test health endpoint
   curl http://localhost:8080/health
   
   # Test API status
   curl http://localhost:8080/api/status
   ```

2. **Test Frontend Pages:**
   - Home: http://localhost:3000/index.html
   - Content Brief: http://localhost:3000/pages/content-brief.html
   - Content History: http://localhost:3000/pages/content-history.html

## Expected Results

### ✅ Successful Integration

**Backend Response (http://localhost:8080/health):**
```json
{
  "status": "healthy",
  "service": "Multi-Lingual Content Creation Agent",
  "version": "1.0.0",
  "timestamp": "2024-01-XX 10:XX:XX UTC"
}
```

**Frontend Test Page:**
- Shows "✅ Backend Connected!"
- Displays backend status information
- Test buttons work without errors

### ❌ Common Issues & Solutions

**Issue: "Backend Connection Failed"**
- **Solution:** Make sure the backend server is running on port 8080
- **Check:** Visit http://localhost:8080/health directly in browser

**Issue: "CORS Error"**
- **Solution:** The frontend server includes CORS headers, but if you're opening HTML files directly (file://), use the Python server instead

**Issue: "Port Already in Use"**
- **Backend:** Change port in `Backend/app.py` (default: 8080)
- **Frontend:** Change PORT in `Frontend/serve.py` (default: 3000)

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors  
- [ ] http://localhost:8080/health returns JSON response
- [ ] http://localhost:8080/api/status returns JSON response
- [ ] http://localhost:3000/test-connection.html shows "Backend Connected"
- [ ] Navigation between frontend pages works
- [ ] Browser console shows no JavaScript errors
- [ ] Test buttons on connection page work

## Next Steps

Once both servers are running and connected:

1. **Explore the Frontend:**
   - Navigate through all pages
   - Check responsive design on different screen sizes
   - Test navigation and routing

2. **Verify Backend Endpoints:**
   - All health endpoints respond correctly
   - API structure is ready for future tasks

3. **Development Workflow:**
   - Keep both servers running during development
   - Backend changes require server restart
   - Frontend changes are served immediately

## Stopping the Servers

- **Backend:** Press `Ctrl+C` in the backend terminal
- **Frontend:** Press `Ctrl+C` in the frontend terminal

## Architecture Overview

```
Frontend (Port 3000)     Backend (Port 8080)
├── index.html          ├── /health
├── pages/              ├── /ready  
├── styles/             ├── /api/status
├── scripts/            └── /api/* (future endpoints)
└── test-connection.html
```

The frontend makes HTTP requests to the backend API, demonstrating the full-stack integration between Task 1 and Task 2.