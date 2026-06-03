from src.retrieval.util import format_prompt
import pandas as pd
import random
import jieba
from src.retrieval.retrieval.retrieval.documents_embedding import DocumentsEmbedding


documentsEmbedding = DocumentsEmbedding()
datas = pd.read_excel('src/retrieval/data/translation_data_end.xlsx').values.tolist()


results_train = []
results_test_zh_2_en = []
results_test_en_2_zh = []

random.shuffle(datas)
print(len(datas))
for i, data in enumerate(datas):
    print(i, '-------------------------------------------------------')
    prompt_en = format_prompt(data[0], False, 4, 0.5, False, documentsEmbedding)
    prompt_zh = format_prompt(data[1], True, 4, 0.5, False, documentsEmbedding)
    
    if i < 1000:
        if len(jieba.lcut(data[1], cut_all=False)) > 10:
            results_test_zh_2_en.append({
                "instruction": prompt_zh,
                "output": data[0]
            })
            
    
        if len(data[0].split(' ')) > 10:
            results_test_en_2_zh.append({
                "instruction": prompt_en,
                "output": data[1]
            })
    else:
        results_train.append({
            "instruction": prompt_en,
            "output": data[1]
        })
        
        
        results_train.append({
            "instruction": prompt_zh,
            "output": data[0]
        })

random.shuffle(results_train)
df = pd.DataFrame(results_train, columns=["instruction", "output"])
df.to_json('train.json', orient='records', force_ascii=False, indent=4)


df = pd.DataFrame(results_test_zh_2_en, columns=["instruction", "output"])
df.to_json('data/results_test_zh_2_en.json', orient='records', force_ascii=False, indent=4)
df = pd.DataFrame(results_test_en_2_zh, columns=["instruction", "output"])
df.to_json('data/results_test_en_2_zh.json', orient='records', force_ascii=False, indent=4)

