from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import routers from your modules
from authenticate import router as auth_router 
from parameter import router as parameter_router
from timeDomain import router as timeseries_router
from fft import router as fft_router

app = FastAPI(title="Vibration API Proxy")

# ---- CORS so Next.js can access ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- REGISTER ROUTERS ----
app.include_router(auth_router)    
app.include_router(parameter_router)
app.include_router(timeseries_router)
app.include_router(fft_router)

@app.get("/health")
def health():
    return {"status": "ok"}

