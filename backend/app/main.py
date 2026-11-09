from fastapi import FastAPI
from backend.app.routes import rentals

app = FastAPI()
app.include_router(rentals.router)

@app.get("/")
def home():
    return {"message": "Drive1 Car Rentals API is running"}