from nltk.translate.bleu_score import sentence_bleu
import jieba
import csv
import json
import pandas as pd
import requests
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.chrf_score import sentence_chrf

smooth = SmoothingFunction()


url_api = "http://IP:PORT/chat"
files = [
         "data/WMT-Chinese-to-English-Machine-Translation-Medical/damo_mt_testsets_zh2en_medical_wmt19.csv",
         "data/WMT-English-to-Chinese-Machine-Translation-Medical/damo_mt_wmt19_medical_en2zh.csv",
    ]


def request_model_api(body):
     response = requests.post(url_api, json=body)  # 使用POST请求

     if response.status_code == 200:  # 判断响应状态码为200表示成功
         resp = json.loads(response.content)
         return resp['content']
     else:
         print("Error occurred while calling the API.")
         return None


for file in files:
    total, total_1, total_2, total_3, total_4, total_5 = 0,0,0,0,0,0
    # with open(file, encoding='utf-8', mode='r') as f:
    #     datas = json.load(f)
    datas = []
    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            if len(row) < 2:
                continue  # 跳过不完整的行
            instruction, output = row[0], row[1]
            datas.append({
                "instruction": instruction,
                "output": output
            })
    print(len(datas))
    new_datas = []
    for m,data in enumerate(datas):
        request_body = {
            "model": "string",
            "query": data['instruction'],
            "is_zh": False if "English-to-Chinese" in file else True, 
            "topk": 4, 
            "fusion_weight": 0.5, 
            "is_es": False
        }
        predict = request_model_api(request_body)
        if "English-to-Chinese" in file:
            pre = jieba.lcut(predict, cut_all=False)
            output = jieba.lcut(data['output'], cut_all=False)
        else:
            pre = predict.split(' ')
            output = data['output'].split(' ')


        total += sentence_chrf(output, pre)
        [score_1, score_2, score_3, score_4] = sentence_bleu([output], pre, weights = [(1,), (1/2, 1/2), (1/3, 1/3, 1/3), (0.25, 0.25, 0.25, 0.25)], smoothing_function=smooth.method4)
        total_1 += score_1
        total_2 += score_2
        total_3 += score_3
        total_4 += score_4

    print(file + '----------------------------------------------------------------------------------------------------------------')
    print("总chrf：", total)
    print("平均chrf：", total / len(datas))
    print("总bleu分数：", total_1, total_2, total_3, total_4)
    print("测试集个数：", len(datas))
    print("平均bleu分数：", total_1 / len(datas), total_2 / len(datas), total_3 / len(datas), total_4 / len(datas))
    print('---------------------------------------------------------------------------------------------------------------------------------')