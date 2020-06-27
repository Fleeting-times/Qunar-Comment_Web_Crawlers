import json
import pandas as pd
from classifiers import DictClassifier


if __name__ == "__main__":
    all = []
    a = DictClassifier()
    data = pd.read_excel('comment.xlsx')
    for d in data.iterrows():
        d = json.loads(d[1].to_json())
        content = d['User_comment']
        sentimen = a.analyse_sentence(content)
        d['sentiment'] = sentimen
        print(d)
        all.append(d)
    pd.DataFrame(all).to_excel('sentiment.xlsx',index=False)


