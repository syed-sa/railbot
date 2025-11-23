from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def chat(payload: dict):
    return {
        "status": "ok",
        "echo": payload
    }
