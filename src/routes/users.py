from fastapi import APIRouter
from fastapi.security import HTTPBearer

user_router = APIRouter(prefix="/user", tags=['users'])

security = HTTPBearer()

@user_router.put('/edit')
async def update_user_info():
    pass




