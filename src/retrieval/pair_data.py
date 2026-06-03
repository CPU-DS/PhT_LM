from .retrieval.retrieval.query import Query


class PairData:
    # def __init__(self, question, is_zh=True, is_es=False) -> None:
    def __init__(self, question, documentsEmbedding, is_zh=True, is_es=False) -> None:
        self.text = Query(question, is_zh)
        self.is_zh = is_zh
        self.is_es = is_es
        
        self.documentsEmbedding=documentsEmbedding

    def get_pair_data(self):
        if self.is_es:
            return self.text.doc_retrieval(self.documentsEmbedding)['source_datas'], [] 
        else:
            return self.text.doc_retrieval(self.documentsEmbedding)['source_datas'], self.text.vec_retrieval(self.documentsEmbedding, self.is_zh)['source_datas']
    
    def get_weight_fusion_resp(self, text, topk, fusion_weight):
        doc_resp, vec_resp = self.get_pair_data()
        if not doc_resp and not vec_resp:
            return []
        
        # 测试集要去除和query一样的句子。训练完模型后和模型合并时需要删除：
        for i, res in enumerate(doc_resp):
            if res['_source']['zh_text'] == text or res['_source']['en_text'] == text:
                del doc_resp[i]
        for i, res in enumerate(vec_resp):
            if res['_source']['zh_text'] == text or res['_source']['en_text'] == text:
                del vec_resp[i]

        # vec_resp = []
        if not doc_resp:
            if len(vec_resp) > topk:
                return vec_resp[:topk]
            else:
                return vec_resp
        if not vec_resp:
            if len(doc_resp) > topk:
                return doc_resp[:topk]
            else:
                return doc_resp
        text_to_source = {}
        vec_k = round(topk * fusion_weight)

        print("vec_k：", vec_k)
        if len(vec_resp) > vec_k:
            for vec_sour in vec_resp[:vec_k]:
                text_to_source[vec_sour['_source']['zh_text'] + vec_sour['_source']['en_text']] = vec_sour
            i = len(text_to_source)
            for doc_sour in doc_resp:
                if i < topk:
                    text_to_source[doc_sour['_source']['zh_text'] + doc_sour['_source']['en_text']] = doc_sour
                    i = len(text_to_source)
            for vec_sour in vec_resp[vec_k:]:
                text_to_source[vec_sour['_source']['zh_text'] + vec_sour['_source']['en_text']] = vec_sour

        else:
            for doc_sour in doc_resp:
                text_to_source[doc_sour['_source']['zh_text'] + doc_sour['_source']['en_text']] = doc_sour

        resp = list(text_to_source.values())[:topk]
        return resp