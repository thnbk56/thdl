from datetime import datetime
from py2neo import Graph, Node, Relationship

months_dict = {'january': 1,
                        'february': 2,
                        'march':  3,
                        'april': 4,
                        'may': 5,
                        'june': 6,
                        'july': 7,
                        'august': 8,
                        'september': 9,
                        'october': 10,
                        'november': 11,
                        'december': 12
                       }

def add_triples_to_neo4j_db(triples):
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "eragold"))
    for triple in triples:
        subj = Node("Person", name=triple[0])
        obj = Node("Entity", name=triple[1])
        re = Relationship.type(triple[2])(subj, obj)
        graph.merge(re, 'Person', 'name')
        
def check_ascii(st):
    for c in st:
        if ord(c) > 255:
            return False
    return True

def check_date_format(st):
    st = st.replace(',', ' ')
    st = st.replace('-', ' ')
    st = st.split(' ')
    cnt = 0
    for x in st:
        if is_num(x):
            if len(x) > 4:
                return False
            if len(x) > 2:
                cnt += 1
        elif len(x) > 0:
            if x.lower() not in months_dict.keys():
                return False
    return cnt < 2
            
def convert_re(re):
    if re.find('per:') != 0:
        return None

    re = re[4:]
    if re == 'cities_of_residence' or re == 'countries_of_residence' or re == 'stateorprovinces_of_residence':
        re = 'place_of_residence'
    elif re == 'city_of_birth' or re == 'country_of_birth' or re == 'stateorprovince_of_birth':
        re = 'place_of_birth'
    elif re == 'city_of_death' or re == 'country_of_death' or re == 'stateorprovince_of_death':
        re = 'place_of_death'
    elif re == 'date_of_birth':
        pass
    elif re == 'date_of_death':
        pass
    elif re == 'origin':
        pass
    elif re == 'religion':
        pass
    elif re == 'schools_attended':
        pass
    elif re == 'title':
        pass
    elif re == 'employee_of':
        pass
    else:
        re = None

    return re

def eliminate_not_digit(st):
    ret = ''
    for c in st:
        if c.isdigit():
            ret += c
    return ret

def eliminate_not_digit_alpha(st):
    ret = ''
    for c in st:
        if c.isdigit() or c.isalpha():
            ret += c
    return ret

def is_num(st):
    try:
        x = int(st)
        return True
    except:
        return False

def st_2_date(st):
    if '-' in st:
        st = st.split('-')
        for i in range(len(st)):
            st[i] = eliminate_not_digit(st[i])
        if len(st) == 3:
            return {'year' : int(st[0]), 'month' : int(st[1]), 'day' : int(st[2])}
        elif st < 3:
            year = None
            month = None
            day = None
            for x in st:
                if len(x) > 2:
                    year = int(x)
                else:
                    if month is None:
                        month = int(x)
                    else:
                        day = int(x)
            return {'year' : year, 'month' : month, 'day' : day}
    else:
        st = st.replace(',', ' ')
        st = st.lower().split(' ')

        year = None
        month = None
        day = None
        for i in range(len(st)):
            st[i] = eliminate_not_digit_alpha(st[i])
        for s in st:
            if len(s) == 0:
                continue
            if not is_num(s):
                if s in months_dict.keys():
                    month = months_dict[s]
                    break
                else:
                    for mst in months_dict.keys():
                        if mst.find(s) == 0:
                            month = months_dict[mst]
                            break
            if month is not None:
                break

        for s in st:
            if len(s) == 0:
                continue
            if is_num(s):
                if len(s) > 2:
                    year = int(s)
                else:
                    if month is None:
                        month = int(s)
                    else:
                        day = int(s)
        return {'year': year, 'month': month, 'day': day}
    return None

def sumarize_dbpedia_triple():
    f = open('dbpedial_triple_set.txt', 'r', encoding='utf-8')
    fo = open('final_dbpedial_triple_set.txt', 'w', encoding='utf-8')
    for line in f:
        if check_ascii(line):
            st = line[2:-2].replace('\"', '\'')
            ents = st.split('\', \'')
            re = convert_re(ents[1])
            if re is not None:
                if 'date' not in re:
                    fo.write(line.replace('per:', ''))

    f = open('dbpedia_convert.txt', "r", encoding="utf-8")
    print('next step')
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
            triple = (st[0], re, st[2])
            fo.write(str(triple) + '\n')
    fo.close()
    print('Done!!')

