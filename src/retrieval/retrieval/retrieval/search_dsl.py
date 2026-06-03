from .documents_embedding import DocumentsEmbedding
from .utils import *

class SearchDSL:
    def __init__(self, query:str,documentsEmbedding,res_from:int=0,res_size:int=10) -> None:
        self.res_from = res_from
        self.res_size = res_size
        self.query = query
        self.documentsEmbedding = documentsEmbedding

    def multi_match(self,fields:list[str]):
        '''
        多字段查询
        '''
        body = {
            "query": {
                "multi_match": {
                    "query": self.query,
                    "fields": fields
                }
            },
            "from": self.res_from,
            "size": self.res_size
        }
        return body

    def vector_search_cos(self, is_zh):
        '''
        向量搜索，余弦相似度
        '''
        if is_zh:
            query_vector = self.documentsEmbedding.query_embedding(self.query)
            body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector,'chunk_vector')+1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            },
            "from": self.res_from,
            "size": self.res_size
        }
        else:
            query_vector = self.documentsEmbedding.query_embedding_en(self.query)
            body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector,'chunk_vector_en')+1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            },
            "from": self.res_from,
            "size": self.res_size
        }
        
        return body














