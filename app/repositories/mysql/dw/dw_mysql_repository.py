from envs.Machine_Learning.Lib.unittest import result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class DWMysqlRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name:str) -> dict[str,str]:
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        rows = result.mappings().fetchall()
        return {row["Field"]: row["Type"] for row in rows}

    async def get_column_values(self, table_name: str, column_name: str,limit:int=10):
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return [row[0] for row in result.fetchall()]

    async def validate_sql(self, sql):
        sql = f"explain {sql}"
        await self.session.execute(text(sql))

    async def run(self, sql)->list[dict]:
        result = await self.session.execute(sql)
        return [dict(row) for row in result.mappings().fetchall()]
