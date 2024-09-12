from sqlalchemy import select, update
from database import ConstantsORM, new_session
from schemas import SConstantsAdd, SConstants, SValues, SResult, SConstantsDict
from solver_function import Solver as solve


class ConstantsRepository:

    @classmethod
    async def add_one(cls, constants: SConstantsAdd) -> int:
        async with new_session() as session:
            consts_dict = constants.model_dump()

            consts = ConstantsORM(**consts_dict)
            session.add(consts)
            await session.flush()
            await session.commit()
            return consts.id

    @classmethod
    async def find_all(cls) -> SConstantsDict:
        async with new_session() as session:
            query = select(ConstantsORM)
            result = await session.execute(query)
            task_models = result.scalars().all()
            task_schemas = [SConstants.model_validate(task_model) for task_model in task_models]
            return SConstantsDict(value=task_schemas)

    @classmethod
    async def get_result(cls, consts_id: int) -> SResult:
        async with new_session() as session:
            query = select(ConstantsORM).filter_by(id=consts_id)
            result = await session.execute(query)
            task_models = result.scalars().all()
            task_schemas = [SConstants.model_validate(task_model) for task_model in task_models]
            task_schemas = task_schemas[0]
            x,y = solve(
                task_schemas.coneHeight,
                task_schemas.cylinderHeight,
                task_schemas.Quefeed,
                task_schemas.Qunderfl,
                task_schemas.Flfeed,
                task_schemas.psolid,
                task_schemas.pfluid,
                task_schemas.muliqour,
            )
            values = [SValues(x=x[i], y=y[i]) for i in range(len(x))]
            result_object = SResult(value=values)
            stmt = update(ConstantsORM).where(ConstantsORM.id == consts_id).values(result=result_object.dict())
            await session.execute(stmt)
            await session.commit()
            return result_object
