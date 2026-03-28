from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pipeline
from routers import pipeline, crud

app = FastAPI(title="BMW Career Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router, prefix="/api")
app.include_router(crud.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
