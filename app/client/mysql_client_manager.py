import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig, app_config


class MYSQLClientManager:
    def __init__(self,config:DBConfig):
        self.engine:AsyncEngine | None = None
        self.config:DBConfig = config
        self.session_factory = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

    def init(self):
        self.engine = create_async_engine(self._get_url(),pool_size = 10,pool_pre_ping=True)
        self.session_factory = async_sessionmaker(bind=self.engine,autoflush=True,expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

dw_mysql_client_manager = MYSQLClientManager(app_config.db_dw)
meta_mysql_client_manager = MYSQLClientManager(app_config.db_meta)

if __name__ == "__main__":
    dw_mysql_client_manager.init()
    async def test():
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            result = await session.execute(text(sql))
            rows = result.mappings().fetchall()
            print(rows)
            print(type(rows))
    asyncio.run(test())