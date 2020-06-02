import requests
from py2neo import Graph, Node, Relationship

from utils import *

graph = Graph("bolt://localhost:7687", auth=("neo4j", "eragold"))

def get_triples(sentence):
    try:
        url = 'http://13.229.140.7:8888'
        data = {'content': sentence}
        response = requests.get(url, params=data)
        res = response.json()
        ret = []
        for tr in res:
            if 'date' in tr[2]:
                ok = True
                for tr2 in ret:
                    if tr2[2] == tr[2]:
                        ok = False
                        break
                if not ok:
                    continue
            if ('date' in tr[2] and check_date_format(tr[1])) or ('date' not in tr[2]):
                ret.append(tr)

        return ret
    except:
        return []

def match_neo4j(person_name, relation):
    try:
        df = graph.run('MATCH (p:Person{name:\'' + person_name + '\'})-[:' + relation + ']->(q) RETURN q.name').to_data_frame()
        res = []
        for i in range(len(df)):
            res.append(df['q.name'].iloc[i])
        return res
    except:
        return []

def check_date(matching_obj_lst, obj):
    obj_date = st_2_date(obj)
    for matching_obj in matching_obj_lst:
        matching_date = st_2_date(matching_obj)
        ok = True
        for t, val in obj_date.items():
            if val is not None:
                matching_val = matching_date[t]
                if matching_val is None or matching_val != val:
                    ok = False
                    break
        if ok:
            return True
    return False

def check_st(matching_obj_lst, obj):
    for st in matching_obj_lst:
        if obj.lower() in st.lower():
            return True
    return False

def check_triples(triples):
    for (subj, obj, relation) in triples:
        matching_obj_lst = match_neo4j(subj, relation)
        if 'date' in relation:
            if not check_date(matching_obj_lst, obj):
                return False
        else:
            if not check_st(matching_obj_lst, obj):
                return False
    return True

def check_fake_news(sentence):
    triples = get_triples(sentence)
    for (subj, obj, relation) in triples:
        matching_obj_lst = match_neo4j(subj, relation)
        if 'date' in relation:
            if not check_date(matching_obj_lst, obj):
                return False
        else:
            if not check_st(matching_obj_lst, obj):
                return False
    return True

def check_fake_news_and_get_triples(sentence):
    triples = get_triples(sentence)
    print('triples: ' + str(triples))
    found_info = False
    for (subj, obj, relation) in triples:
        matching_obj_lst = match_neo4j(subj, relation)
        if len(matching_obj_lst) > 0:
            found_info = True
        if 'date' in relation:
            if not check_date(matching_obj_lst, obj):
                return False, found_info, triples
        else:
            if not check_st(matching_obj_lst, obj):
                return False, found_info, triples
    return True, found_info, triples

# print(get_triples('Barack Obama (born August 4, 1961) is an American politician'))

# print(check_fake_news('Alfred J. Lewy, a.k.a. "Sandy Lewy", is an American sleep researcher. '))
# print(check_fake_news('Barack Obama (born August 4, 1961) is an American politician and attorney who served as the 44th president of the United States from 2009 to 2017'))
