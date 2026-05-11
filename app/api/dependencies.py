from typing import Annotated

from fastapi import Depends
from langchain_community.embeddings import DashScopeEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app.client.embedding_client_manager import embedding_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricsQdrantRepository
from app.services.query_service import QueryService

async def get_meta_session():
    async with meta_mysql_client_manager.session_factory() as session:
        yield session

async def get_dw_session():
    async with dw_mysql_client_manager.session_factory() as session:
        yield session

async def get_column_qdrant_repository()->ColumnQdrantRepository:
    return ColumnQdrantRepository(qdrant_client_manager.client)

async def get_meta_mysql_repository(session:Annotated[AsyncSession,Depends(get_meta_session)])->MetaMysqlRepository:
    return MetaMysqlRepository(session)

async def get_dw_mysql_repository(session:Annotated[AsyncSession,Depends(get_dw_session)])->DWMysqlRepository:
    return DWMysqlRepository(session)

async def get_embedding_client()->DashScopeEmbeddings:
    return embedding_client_manager.client

async def get_value_es_repository()->ValueEsRepository:
    return ValueEsRepository(es_client_manager.client)

async def get_metric_qdrant_repository()->MetricsQdrantRepository:
    return MetricsQdrantRepository(qdrant_client_manager.client)

async def get_query_service(
        column_qdrant_repository: Annotated[ColumnQdrantRepository,Depends(get_column_qdrant_repository)],
        embedding_client: Annotated[DashScopeEmbeddings,Depends(get_embedding_client)],
        metric_qdrant_repository: Annotated[MetricsQdrantRepository,Depends(get_metric_qdrant_repository)],
        value_es_repository: Annotated[ValueEsRepository,Depends(get_value_es_repository)],
        meta_mysql_repository: Annotated[MetaMysqlRepository,Depends(get_meta_mysql_repository)],
        dw_mysql_repository: Annotated[DWMysqlRepository,Depends(get_dw_mysql_repository)],
)->QueryService:
    return QueryService(
        meta_mysql_repository=meta_mysql_repository,
        dw_mysql_repository=dw_mysql_repository,
        column_qdrant_repository=column_qdrant_repository,
        embedding_client=embedding_client,
        metric_qdrant_repository=metric_qdrant_repository,
        value_es_repository=value_es_repository,
    )