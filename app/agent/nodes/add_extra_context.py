from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.core.log import logger

async def add_extra_context(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress","step":"添加额外上下文","status":"running"})

    try:
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = (today.month - 1) // 3 + 1
        date_info = DateInfoState(
            date=date_str,
            weekday=weekday,
            quarter=f"Q{quarter}",
        )

        db_info = DBInfoState(
            dialect="mysql",
            version="8.0.46"
        )
        writer({"type": "progress", "step": "添加额外上下文", "status": "success"})
        logger.info(f"数据库信息{db_info}")
        logger.info(f"日期信息{date_info}")
        return {"db_info": db_info, "date_info": date_info}
    except Exception as e:
        logger.error(f"添加额外上下文失败:{e}")
        writer({"type": "progress", "step": "添加额外上下文", "status": "error"})
        raise
