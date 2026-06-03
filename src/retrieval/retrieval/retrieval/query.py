
from .kb import DocKB, ESVectorKB
from .search_dsl import SearchDSL
from .config import TEXT_FIELDS, KB_NAME, VEC_NAME

class Query:
    def __init__(self, text, is_zh):
        self.text = text
        self.kb_name = KB_NAME
        self.vec_name = VEC_NAME
        self.text_fields =  TEXT_FIELDS[0] if is_zh else TEXT_FIELDS[1]

    def doc_retrieval(self, documentsEmbedding, res_from=0, res_size=10):
        dsl = SearchDSL(self.text,documentsEmbedding,res_from, res_size).multi_match([self.text_fields])
        resp = DocKB(self.kb_name).query_by_dsl(dsl)
        return resp

    def vec_retrieval(self, documentsEmbedding, is_zh, res_from=0, res_size=10):
        dsl = SearchDSL(self.text, documentsEmbedding,res_from, res_size).vector_search_cos(is_zh)
        veckb, dockb = ESVectorKB(self.vec_name), DocKB(self.kb_name)
        resp = veckb.query_by_dsl(dsl, dockb)
        return resp

