# Memory Systems Frontend

Angular frontend for comparing Mem0 and Zep memory systems.

## Features

- **Two input fields**: User ID and Query
- **Side-by-side comparison**: Zep vs Mem0 responses
- **Memory retrieval display**: Shows what memories were retrieved
- **Conversation history**: Each query/response pair is preserved
- **Real-time updates**: Both systems queried simultaneously

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend is running on `http://localhost:8000`

3. Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:4200`

## Usage

1. Enter a User ID (defaults to "demo_user_123")
2. Enter a query in the text field
3. Click "Submit Query" or press Enter
4. View responses from both systems side-by-side
5. See what memories were retrieved for context
6. Query field resets for next input

## Architecture

- **AppComponent**: Main component with form and two-column layout
- **MemoryService**: HTTP service for API calls to backend
- **Responsive design**: Works on desktop and mobile
- **Error handling**: Displays errors from backend API
- **Loading states**: Shows loading indicators during requests

The frontend makes parallel calls to both `/mem0/query` and `/zep/query` endpoints and displays results in real-time.