import json
from typing import Any

from langchain_community.embeddings import DashScopeEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricsQdrantRepository


class QueryService:
    def __init__(self,
    column_qdrant_repository: ColumnQdrantRepository,
    embedding_client: DashScopeEmbeddings,
    metric_qdrant_repository: MetricsQdrantRepository,
    value_es_repository: ValueEsRepository,
    meta_mysql_repository: MetaMysqlRepository,
    dw_mysql_repository: DWMysqlRepository,
    ):
        self.column_qdrant_repository: ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client: DashScopeEmbeddings = embedding_client
        self.metric_qdrant_repository: MetricsQdrantRepository = metric_qdrant_repository
        self.value_es_repository: ValueEsRepository = value_es_repository
        self.meta_mysql_repository: MetaMysqlRepository = meta_mysql_repository
        self.dw_mysql_repository: DWMysqlRepository = dw_mysql_repository
        pass
    async def query(self, query: object):
        state = DataAgentState(query=query)
        context = DataAgentContext(
            column_qdrant_repository=self.column_qdrant_repository,
            embedding_client=self.embedding_client,
            metric_qdrant_repository=self.metric_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository
        )
        try:
            async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n" # SSE格式发送数据
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n"