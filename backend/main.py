from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # <-- ADDED import
from routers import auth, projects, scan

app = FastAPI()

origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ADDED: Mount the screenshots directory to serve images ---
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")
# -----------------------------------------------------------

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(scan.router) 

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aura Accessibility Scanner API"}