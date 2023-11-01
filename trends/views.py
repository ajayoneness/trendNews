from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pytrends.request import TrendReq
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import spacy
from string import punctuation
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS
import random


def home(request):
    return render(request, 'home.html')



#to get the google trends topic
def today_tranding_topic( country_name='india'):
    pytrends = TrendReq()
    df = pytrends.trending_searches(pn=country_name)
    return str(df[0][0])

print("query : " + today_tranding_topic())



#find the top google serach urls
def get_googlesearch_link(topic, no_of_url=20):
    if topic == "":
        query = today_tranding_topic()
    else:
        query = str(topic)



    search_results = search(query, num_results=no_of_url)
    lis = []
    for url in search_results:
        lis.append(url)
    return lis

#print(get_googlesearch_link())



#scrap news paragraph
def scrapallparagraph(url, tag, n):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        data = soup.find_all(tag)
        par = ""
        for i in range(0, n):
            try:
                if len(str(data[i].text.strip())) > 100:
                    par = par + f"{str(data[i].text.strip())}"
            except:
                break
        return par



def calculate_word_frequency(doc):
    stopwords = list(STOP_WORDS)
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_frequencies:
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    return word_frequencies



def find_sentence_tokens(doc):
    return [sent for sent in doc.sents]

def find_sentence_scores(doc):
    sentence_tokens = find_sentence_tokens(doc)
    word_frequencies = calculate_word_frequency(doc)
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    return sentence_scores


#get the summery of all the news
def find_summary(text, content_length=0.3):
    doc = spacy.load('en_core_web_sm')(text)
    select_length = int(len(find_sentence_tokens(doc)) * content_length)
    sentence_score = find_sentence_scores(doc)
    summary = nlargest(select_length, sentence_score, key=sentence_score.get)
    final_summary = [word.text for word in summary]
    return ' '.join(final_summary)








class ProcessStringView(APIView):
    def post(self, request):
        input_string = request.data.get('input_string', '')

        allurls = get_googlesearch_link(input_string)

        urls = random.sample(allurls, 5)
        print("randomError : ", urls)

        allnews = []
        for url in urls:
            news = scrapallparagraph(url, "p", 10)
            if news != "":
                allnews.append(news)

        # all news contains all the news scrap from different sites in list
        # print(allnews)

        allnewsinstr = ""

        for news in allnews:
            allnewsinstr = allnewsinstr + news

        # allnewsinstr contain all the news in single string
        # print(allnewsinstr)

        # summarize the news using textrank algorithm
        summary = find_summary(allnewsinstr)
        # print('NEW Content : ' + summary)

        processed_string = summary

        if input_string == "":
            query = today_tranding_topic()
        else:
            query = input_string

        return Response({'output_string': processed_string, "topic": query }, status=status.HTTP_200_OK)



class getNewsTopic(APIView):
    def get(self, request):
        query = today_tranding_topic
        return Response({"topic": query }, status=status.HTTP_200_OK)

