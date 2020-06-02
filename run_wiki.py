# from triple import *
from check_fake_news import *
from wiki_crawler import *
from py2neo import Graph, Node, Relationship

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

def add_triples_to_neo4j(triples):
    for triple in triples:
        subj = Node("Person", name=triple[0])
        obj = Node("Entity", name=triple[1])
        re = Relationship.type(triple[2])(subj, obj)
        graph.merge(re, 'Person', 'name')

def run_wiki_case():
    f = open('data/dbpedia/final_dbpedial_triple_set.txt', 'r')
    people_name_lst = set()
    for line in f:
        x = line.replace('\"', '\'')
        y = x[2:-2].split('\', \'')
        people_name_lst.add(y[0])
    f.close()
    marked_name_lst = set()
    try:
        f = open('data/dbpedia/marked_name_lst.txt', 'r')
        for line in f:
            marked_name_lst.add(line.replace('\n', ''))
        f.close()
    except:
        pass

    print('nb people = ', len(people_name_lst), ' nb marked = ', len(marked_name_lst))

    cnt = 0
    true_cnt = 0
    for name in people_name_lst:
        cnt += 1
        print(cnt)
        if name not in marked_name_lst:
            try:
                intro = get_introduction(name)
                intro = intro.split('.')[0]
                print(intro)
                is_not_fake_new, found_info, triples = check_fake_news_and_get_triples(intro)
                if is_not_fake_new:
                    true_cnt += 1
                add_triples_to_neo4j(triples)
                fmark = open('data/dbpedia/marked_name_lst.txt', 'a')
                fmark.write(name + '\n')
                fmark.close()
                fres = open('data/dbpedia/result_check_fake_new.txt', 'a')
                fres.write(name + ';' + str(is_not_fake_new) + '\n')
                fres.close()
            except:
                pass

    print('Ty le dung la: ', 100 * (true_cnt / cnt))

run_wiki_case()
