# Memory Systems Comparison Demo

A full-stack web application that provides a side-by-side comparison of two AI memory systems: **Mem0** and **Zep**. Built with FastAPI backend and Angular frontend, featuring a modern MongoDB-inspired design.

## 🚀 Features

- **Side-by-Side Comparison**: Query both Mem0 and Zep memory systems simultaneously
- **Real-Time Responses**: Parallel API calls for fast comparison
- **Memory Visualization**: Retrieved memories displayed as clean bulleted lists
- **Modern UI**: MongoDB-inspired color scheme with gradients and animations
- **Responsive Design**: Works on desktop and mobile devices
- **Conversation History**: Maintains query/response history for each system
- **Error Handling**: Comprehensive error reporting and loading states

## 🏗️ Architecture

```
superdemo/
├── backend/          # FastAPI REST API
│   ├── main.py       # Main application with endpoints
│   ├── requirements.txt
│   └── README.md
└── frontend/         # Angular web application
    ├── src/
    │   ├── app/      # Angular components and services
    │   └── styles.css # MongoDB-inspired styling
    ├── package.json
    └── README.md
```

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Endpoints**: 
  - `POST /mem0/query` - Query Mem0 memory system
  - `POST /zep/query` - Query Zep memory system
  - `GET /health` - Health check
- **Memory Integration**: Direct integration with Mem0 and Zep APIs
- **CORS**: Configured for frontend communication

### Frontend (Angular)
- **Framework**: Angular 17 with standalone components
- **UI Library**: Custom CSS with MongoDB color palette
- **State Management**: RxJS for API calls and state handling
- **Memory Display**: Dynamic bulleted lists for retrieved memories

## 🎨 Design

The UI features a **MongoDB-inspired design** with:
- **Dark gradient backgrounds** (#001E2B to #00684A)
- **MongoDB green accents** (#00684A, #00ED64)
- **Clean white cards** with subtle shadows
- **Smooth animations** and hover effects
- **Professional typography** with proper hierarchy

## 🛠️ Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **API Keys** for:
  - OpenAI (for LLM responses)
  - Mem0 (for Mem0 memory system)
  - Zep (for Zep memory system)

## 📦 Installation & Setup

### 1. Clone Repository
```bash
cd competitive/superdemo
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export MEM0_API_KEY="your-mem0-api-key"
export ZEP_API_KEY="your-zep-api-key"

# Start backend server
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:4200`

## 🚀 Usage

1. **Open the application** in your browser at `http://localhost:4200`

2. **Enter a User ID** (defaults to "demo_user_123")

3. **Enter your query** in the text field

4. **Click "Submit Query"** or press Enter

5. **View the results** side-by-side:
   - **Left Column**: Zep memory system response and retrieved memories
   - **Right Column**: Mem0 memory system response and retrieved memories

6. **Continue the conversation** - memories accumulate over time for more personalized responses

## 📊 Memory Systems Comparison

### Mem0
- **Approach**: Direct fact extraction and storage
- **Strengths**: Excellent at remembering specific details
- **Memory Format**: Structured facts (e.g., "User name is John")

### Zep
- **Approach**: Graph-based knowledge relationships
- **Strengths**: Contextual understanding and connections
- **Memory Format**: Relationship-based facts (e.g., "John likes pizza")

## 🔧 API Reference

### Query Request Format
```json
{
  "user_id": "string",
  "query": "string"
}
```

### Query Response Format
```json
{
  "response": "AI generated response",
  "memory_saved": true,
  "context_found": false,
  "retrieved_memory": ["memory item 1", "memory item 2"]
}
```

## 🧪 Testing

### Backend Testing
```bash
# Health check
curl http://localhost:8000/health

# Test Mem0 endpoint
curl -X POST http://localhost:8000/mem0/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "Hello"}'

# Test Zep endpoint  
curl -X POST http://localhost:8000/zep/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "Hello"}'
```

### Frontend Testing
- Navigate to `http://localhost:4200`
- Test form submission and response display
- Verify memory bulleted lists appear correctly
- Test responsive design on different screen sizes

## 🔍 Troubleshooting

### Backend Issues
- **API Key Errors**: Ensure all environment variables are set correctly
- **Import Errors**: Verify all dependencies are installed with `pip install -r requirements.txt`
- **CORS Errors**: Check that frontend origin is allowed in CORS settings

### Frontend Issues
- **Compilation Errors**: Run `npm install` to ensure dependencies are current
- **API Connection**: Verify backend is running on `http://localhost:8000`
- **Styling Issues**: Clear browser cache and refresh

## 🚀 Deployment

### Backend Deployment
- Use environment variables for API keys (never commit keys to git)
- Deploy to platforms like Heroku, Railway, or AWS
- Ensure CORS settings include production frontend URL

### Frontend Deployment
- Build production version: `ng build --prod`
- Deploy to platforms like Netlify, Vercel, or AWS S3
- Update API base URL for production backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of a competitive analysis of memory systems and is intended for research and evaluation purposes.

---

**Built with ❤️ using FastAPI, Angular, and AI memory systems**