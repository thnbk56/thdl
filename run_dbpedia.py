from py2neo import Graph, Node, Relationship
from utils import *
from check_fake_news import *

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

def add_triples_to_neo4j(triples):
    for triple in triples:
        subj = Node("Person", name=triple[0])
        obj = Node("Entity", name=triple[1])
        re = Relationship.type(triple[2])(subj, obj)
        graph.merge(re, 'Person', 'name')

def run_dbpedia_case():
    f = open('data/dbpedia/dbpedia_raw.txt', "r", encoding="utf-8")
    fo = open('data/dbpedia/final_dbpedial_triple_set.txt', 'w', encoding='utf-8')
    for line in f:
        st = line[0: -1].split(';')
        re = st[1]
        if re != 'description':
            if re == 'deathDate':
                re = 'date_of_death'
            elif re == 'birthDate':
                re = 'date_of_birth'
            elif re == 'deathPlace':
                re = 'place_of_death'
            elif re == 'birthPlace':
                re = 'place_of_birth'
            triple = (st[0], st[2], re)
            fo.write(str(triple) + '\n')
            add_triples_to_neo4j(triple)
        else:
            sentence = line.replace(';description;', ' is ')
            result = get_triples(sentence)
            if result is not None:
                for tr in result:
                    fo.write(str(tr) + '\n')
                    add_triples_to_neo4j(tr)
    fo.close()


run_dbpedia_case()