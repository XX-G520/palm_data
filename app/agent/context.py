from typing import TypedDict

from langchain_community.embeddings import DashScopeEmbeddings

from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricsQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository:ColumnQdrantRepository
    embedding_client:DashScopeEmbeddings
    metric_qdrant_repository:MetricsQdrantRepository
    value_es_repository:ValueEsRepository
    meta_mysql_repository:MetaMysqlRepository
    dw_mysql_repository:DWMysqlRepository