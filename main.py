from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import google.generativeai as genai

# Configure the Gemini AI
genai.configure(api_key='AIzaSyCgZxMbdMmYVyo2zTK-J-6GRLYcGdGHYWQ')

# Set up the model
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    chat = model.start_chat(history=[])
    
    try:
        await manager.send_personal_message("Hello! I'm Preciouse, Your Mental HealthCare Assistant. How are you feeling today?", websocket)
        
        while True:
            data = await websocket.receive_text()
            if data.lower() in ['exit', 'quit', 'bye']:
                await manager.send_personal_message("Preciouse: Take care! Remember, it's okay to seek help if you need it.", websocket)
                break
            
            # Generate response using Gemini
            response = chat.send_message(f"User: {data}\nRespond as a supportive mental health chatbot:")
            
            await manager.send_personal_message(f"Mental Health Bot: {response.text}", websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Client left the chat")

