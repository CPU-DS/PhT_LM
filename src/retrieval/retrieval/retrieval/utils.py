import time
import pandas as pd
import re

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('{}共耗时约 {:.2f} 秒'.format(func, time.time() - start))
        return res
    return wrapper

def excel_parser(file):
    df = pd.read_excel(file, sheet_name=None)
    pair_datas = []
    for sheet in df.keys():
        df_sheet = df[sheet].fillna('')
        pair_datas += df_sheet.to_dict(orient='records')
    return pair_datas

def result_2_text(result):
    source_datas = []
    for hit in result['hits']['hits']:
        id = hit['_id']
        score = hit['_score']
        source = hit['_source']
        source_datas.append({"_id":id,"_score":score,"_source":source})
    resp = {"total": 100, "source_datas": source_datas}
    return resp

def vec_2_text(result,from_kb):
    source_datas = []
    for hit in result['hits']['hits']:
        id = hit['_id']
        score = hit['_score']
        source =  from_kb.query_by_id(id)['_source']
        source_datas.append({"_id":id,"_score":score,"_source":source})
    resp = {"total": 100, "source_datas": source_datas}
    return resp


