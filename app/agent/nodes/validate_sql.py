from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.repositories.mysql.dw.dw_mysql_repository import DWMysqlRepository
from app.core.log import logger

async def validate_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress","step":"校验sql","status":"running"})

    try:
        sql = state["sql"]

        dw_mysql_repository:DWMysqlRepository = runtime.context["dw_mysql_repository"]

        try:
            await dw_mysql_repository.validate_sql(sql)
            writer({"type": "progress", "step": "校验sql", "status": "success"})

            logger.info("校验sql成功")
            return {'error': None}
        except Exception as e:
            writer({"type": "progress", "step": "校验sql", "status": "success"})

            logger.info("校验SQL报错")
            return {'error': str(e)}
    except Exception as e:
        logger.error(f"抽取关键词失败:{e}")
        writer({"type": "progress", "step": "校验sql", "status": "error"})
        raise
