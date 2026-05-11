from langgraph.runtime import Runtime
from sqlalchemy import text

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def run_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress","step":"执行sql","status":"running"})

    try:
        sql = state['sql']

        dw_mysql_repository = runtime.context['dw_mysql_repository']

        result = await dw_mysql_repository.run(text(sql))

        writer({"type": "progress", "step": "执行sql", "status": "success"})


        logger.info(f"结果：{result}")
        writer({"type":"result","data":result})
    except Exception as e:
        logger.error(f"抽取关键词失败:{e}")
        writer({"type": "progress", "step": "执行sql", "status": "error"})
        raise
