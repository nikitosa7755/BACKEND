from typing import Annotated
from fastapi import APIRouter, Depends
from repository import ConstantsRepository
from schemas import SConstantsAdd, SConstantsID, SResult, SConstantsDict


router = APIRouter(
    prefix="/constants",
    tags=["Крутое API"],
)


@router.get("/add")
async def add_consts(
        task: Annotated[SConstantsAdd, Depends()],
) -> SConstantsID:
    consts_id = await ConstantsRepository.add_one(task)
    return {"ok": True, "consts_id": consts_id}


@router.get("/get")
async def get_constants() -> SConstantsDict:
    constants = await ConstantsRepository.find_all()
    return constants


@router.get("/result")
async def get_result(
        consts_id: int
) -> SResult:
    result = await ConstantsRepository.get_result(consts_id)
    return result
