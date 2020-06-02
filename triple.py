import nltk
from pycorenlp import *
import collections
import pprint
# from neuralcoref import Coref
import re
import pprint
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
# from models import db
import csv
import os

import pandas as pd

from utils import *

# people_df = pd.read_csv('people_wiki.csv', encoding='utf-8')
# people_set = set()
# for i in range(len(people_df)):
#     name = people_df['name'].iloc[i]
#     people_set.add(name)

pp = pprint.PrettyPrinter(indent=4)

from stanfordcorenlp import StanfordCoreNLP

from extract_tacred_bert_softmax import extract

from nltk.tokenize import sent_tokenize

nlp = StanfordCoreNLP('./stanford-corenlp')

def NER(sentence):

    tokens = nlp.word_tokenize(sentence)
    # print("NER ", sentence)
    ner = nlp.ner(sentence)
    # print(ner)
    entities = []
    entity = ''
    pos = []
    i = 0
    lasttype = 'O'
    for n in ner:
        if n[1] == 'O':
            if len(entity) != 0:
                e = {}
                pos.append(i-1)
                e['name'] = entity
                e['pos'] = pos
                entities.append(e)
                entity = ''
                pos = []
        else:
            if n[1] != lasttype:
                if lasttype == 'O':
                    entity = n[0]
                    pos = [i]
                    lasttype = n[1]
                    i = i + 1
                    continue
                e = {}
                pos.append(i-1)
                e['name'] = entity
                e['pos'] = pos
                entities.append(e)
                entity = n[0]
                pos = [i]
            else:
                entity = entity + ' ' + n[0]
        lasttype = n[1]
        i = i + 1
    if lasttype != 'O' and entity not in entities and len(entity) != 0:
        e = {}
        pos.append(i-1)
        e['name'] = entity
        e['pos'] = pos
        entities.append(e)
    # print(entities)
    return tokens, entities
#
def triple(sentence):
    original_sentence = sentence
    # sentence = neuralcorefIt(sentence)
    sents = sent_tokenize(sentence)
    results = set()
    cnt = 0
    for sent in sents:
        cnt += 1
        if cnt > 5:
            break
        tokens, entities = NER(sent)
        # print(entities)
        if (len(entities)) <= 1:
            continue
        maxscore = -1
        result = []
        for i in range(0, len(entities)):
            # print(entities[i]['name'], entities[i]['name'] in people_set, original_sentence.find(entities[i]['name']))
            if not(original_sentence.find(entities[i]['name']) == 0):
                continue
            for j in range(0, len(entities)):
                if i == j:
                    continue
                query = {}
                query['token'] = tokens
                query['relation'] = 'per:title'
                query['h'] = {}
                query['h']['name'] = entities[i]['name']
                query['h']['pos'] = entities[i]['pos']
                query['t'] = {}
                query['t']['name'] = entities[j]['name']
                query['t']['pos'] = entities[j]['pos']
                pred, score = extract(query)
                pred = convert_re(pred)
                if pred is not None:
                    result.append((entities[i]['name'], entities[j]['name'], pred)) #,score
        if len(result) > 0:
            for tr in result:
                results.add(tr)
            # results += result

    return [[x, y, z] for (x, y, z) in results]


if __name__ == '__main__':
    sentence = "Digby Morrell (born 10 October 1979) is a former Australian rules footballer who played with the Kangaroos and Carlton in the Australian Football League (AFL)."
    triples = triple(sentence)
    print('triples:')
    print(triples)
    nlp.close()


#
#
# import spacy
# nlp_spacy = spacy.load('en')
#
# import neuralcoref
# neuralcoref.add_to_pipe(nlp_spacy)
#
# caps = "([A-Z])"
# prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
# suffixes = "(Inc|Ltd|Jr|Sr|Co)"
# starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
# acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
# websites = "[.](com|net|org|io|gov)"
# # coref = Coref()
#
# #Make sure sentence is in good format.
# #Source code from: https://stackoverflow.com/questions/4576077/python-split-text-on-sentences/9047421#9047421
# def split_into_sentences(text):
#     text = " " + text + "  "
#     text = text.replace("\n"," ")
#     text = re.sub(prefixes,"\\1<prd>",text)
#     text = re.sub(websites,"<prd>\\1",text)
#     if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
#     text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
#     text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
#     text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
#     text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
#     text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
#     text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
#     text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
#     if "”" in text: text = text.replace(".”","”.")
#     if "\"" in text: text = text.replace(".\"","\".")
#     if "!" in text: text = text.replace("!\"","\"!")
#     if "?" in text: text = text.replace("?\"","\"?")
#     text = text.replace(".",".<stop>")
#     text = text.replace("?","?<stop>")
#     text = text.replace("!","!<stop>")
#     text = text.replace("<prd>",".")
#     sentences = text.split("<stop>")
#     sentences = sentences[:-1]
#     sentences = [s.strip() for s in sentences]
#     return sentences
#
# def nomalize(text):
#     text = " " + text + "  "
#     text = text.replace("\n"," ")
#     text = re.sub(prefixes,"\\1<prd>",text)
#     text = re.sub(websites,"<prd>\\1",text)
#     if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
#     text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
#     text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
#     text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
#     text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
#     text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
#     text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
#     text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
#     if "”" in text: text = text.replace(".”","”.")
#     if "\"" in text: text = text.replace(".\"","\".")
#     if "!" in text: text = text.replace("!\"","\"!")
#     if "?" in text: text = text.replace("?\"","\"?")
#     text = text.replace(".",".<stop>")
#     text = text.replace("?","?<stop>")
#     text = text.replace("!","!<stop>")
#     text = text.replace("<prd>",".")
#     return text.replace("<stop>", "")
#
#
# #Resolve coreference in text using neuracoref
# def neuralcorefIt(text):
#     # sentences = split_into_sentences(text)
#     # sentences[0] = sentences[0].capitalize()
#     # for s in sentences:
#     # 	if s[-1] == '?':
#     # 		sentences.remove(s)
#
#     text = nomalize(text)
#     doc = nlp_spacy(text)
#     doc._.has_coref  ## True
#     doc._.coref_clusters  ## [My sister: [My sister, She], a dog: [a dog, him]]
#     return doc._.coref_resolved
#
#
#
