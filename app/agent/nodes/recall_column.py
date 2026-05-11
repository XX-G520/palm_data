
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def recall_column(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type":"progress","step":"召回字段","status":"running"})

    try:
        keywords = state['keywords']
        column_qdrant_repository = runtime.context['column_qdrant_repository']
        query = state['query']
        embedding_client = runtime.context['embedding_client']
        # 先借助大模型扩展提示词中的关键词

        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({'query': query})
        keywords = set(keywords + result)
        
        column_info_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            current_column_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding,
                                                                                           score_threshold=0.6,
                                                                                           limit=10)
            for column_info in current_column_infos:
                if column_info.id not in column_info_map:
                    column_info_map[column_info.id] = column_info
        retrieved_column_infos: list[ColumnInfo] = list(column_info_map.values())

        writer({"type": "progress", "step": "召回字段", "status": "success"})

        logger.info(f"检索到字段信息{list(column_info_map.keys())}")
        return {"retrieved_column_infos": retrieved_column_infos}
    except Exception as e:
        logger.error(f"抽取关键词失败:{e}")
        writer({"type": "progress", "step": "合并召回信息", "status": "error"})
        raise
