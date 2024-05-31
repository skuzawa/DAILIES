from fastapi import APIRouter
from fastapi import Request,Response,HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas import Daily,DailyBody,SuccessMsg
from starlette.status import HTTP_201_CREATED
from database import db_create_daily,db_get_single_daily,db_get_daily,db_delete_daily,db_update_daily
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()

@router.post("/api/daily",response_model=Daily)
async def create_daily(request: Request,response: Response, data:DailyBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers
    )
    daily = jsonable_encoder(data)
    res = await db_create_daily(daily)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(
        key = "access_token",value=f"Bearer {new_token}" , httponly=True, sametime="none" secure=True
    )
    if res:
        return res
    raise HTTPException(
        status_code = 404, detail="Created task failed"
    )

@router.get("/api/daily", response_model=List[Daily])
async def get_dailies(request : Request):
    #auth.verify_jwt(request)
    res = await db_get_daily()
    return res

@router.get("/api/daily/{id}", response_model=Daily)
async def get_single_daily(request:Request,response:Response, id: str):
    new_token,_ = auth.verify_csrf_update_jwt(request)
    res = await db_get_single_daily(id)
    response.set_cookie(
        key="access_token",value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True
    )
    if res:
        return res
    raise HTTPException(
        status_code=404,detail=f"Daily of ID:{id} doesn't exist"
    )

@router.put("/api/daily/{id}",response_model=Daily)
async def update_daily(request:Request,response:Response,id:str,data:DailyBody, csrf_protect:CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request,csrf_protect,request.headers
    )
    daily = jsonable_encoder(data)
    res = await db_update_daily(id,daily)
    response.set_cookie(
        key="access_token",value=f"Bearer {new_token}", httponly=True, samesite="none" ,secure=True
    )
    if res:
        return res
    raise HTTPException(
        status_code=404,detail="Update daily failed"
    )

@router.delete("/api/daily/{id}",response_model=SuccessMsg)
async def delete_daily(request:Request,response:Response,id:str, csrf_protect:CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request,csrf_protect,request.headers
    )
    res = await db_delete_daily(id)
    response.set_cookie(
        key="access_token",value=f"Bearer {new_token}", httponly=True, samesite="none" ,secure=True
    )
    if res:
        return {"message":"Successfully deleted"}
    raise HTTPException(
        status_code=404, detail="Deleted daily failed"
    )