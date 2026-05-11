import asyncio

from langchain_community.embeddings import DashScopeEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self,config:EmbeddingConfig):
        self.config : EmbeddingConfig = config
        self.client : DashScopeEmbeddings | None = None

    def init(self):
        self.client = DashScopeEmbeddings(
            model=self.config.model,
        )
embedding_client_manager = EmbeddingClientManager(app_config.embedding)
if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client
    async def test():
        text = "what is deep learning?"
        batch_embeddings = await client.aembed_documents(["11111","22222","33333","44444","55555","66666","77777","88888","99999","0000000"])
        print(batch_embeddings)
        query_result = await client.aembed_query(text)
        print(query_result)
    asyncio.run(test())