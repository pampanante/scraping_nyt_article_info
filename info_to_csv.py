from urllib2 import urlopen
from calendar import monthrange
from math import trunc
import json
import codecs
import requests
import csv


base_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.'
search_query = 'your_search_query'

response_format = 'json'
api_key=''

api_f = open('nytapikey.txt','r')
for line in api_f:
    api_key = line
    break;

#test call
test_json = call_the_articles('20000101','20000125')
for i in range(0,10):
    print test_json['response']['docs'][2]['pub_date'][i]

def call_the_articles(search_begin_date,search_end_date):
    url = base_url+response_format+"?q="+search_query+"&begin_date="+search_begin_date+"&end_date="+search_end_date+"&api-key="+api_key
    return json.loads(urlopen(url).read())


def scrape_urls(begin_year,end_year,start_month,end_month,density):
    paired_data = {'dates' : [], 'urls':[],'headlines':[]}
    
    for year in range(begin_year,end_year,density):
        
        for i in range(start_month,end_month+1):
            
            call_num = trunc(30/density)
            
            for j in range(call_num):
                
                s_day = j*density +1
                e_day = s_day + density-1
                if j == call_num-1:
                    e_day = get_monthrange(year,i)
                start_day = generate_date(year,i,s_day)
                end_day = generate_date(year,i,e_day)
                
                # it ignores the case of '0', and more than '10' in the period.
                try:
                    partial_article = call_the_articles(start_day,end_day) 
                
                    hit_num = int(partial_article['response']['meta']['hits'])
                
                    
                    for article_num in range(hit_num):
                        
                        paired_data['dates'].append(partial_article['response']['docs'][article_num]['pub_date'])
                        paired_data['urls'].append(partial_article['response']['docs'][article_num]['web_url'])    
                        paired_data['headlines'].append(partial_article['response']['docs'][article_num]['headline']['main'].encode('ascii', 'ignore'))
 
                
                except:
                
                    # need better solution
                
                    print "article number is weird in this period " + start_day + " ~ " + end_day
                    print  "hit is " + str(hit_num)

                    
    return paired_data


# returns dates in the form api requires

def generate_date(year,month,day):
    if month < 10 :
        month = "0" + str(month)
    else :
        month = str(month)
    if day < 10 :
        day = "0" + str(day)
    else :
        day = str(day)
        
    return str(year) + month + day

#returns last day of each month
def get_monthrange(year,month):
    return monthrange(year,month)[1]



#better not to do more than one year at the same time.

begin_year = 1992

article_data = scrape_urls(begin_year, begin_year+1,1,12,10)

with open('data/aritlces_'+ str(begin_year)+'.csv', 'wb') as csvfile:
    
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, escapechar='"')
    
    for i in range(len(article_data['urls'])):
        csvwriter.writerow([article_data['urls'][i]] + [article_data['dates'][i]] + [article_data['headlines'][i]])

     
   