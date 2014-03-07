from urllib2 import urlopen
from calendar import monthrange
from math import trunc
import json
import codecs
import requests



base_url = "http://api.nytimes.com/svc/search/v2/articlesearch."
search_query = 'gentrification'

response_format = 'json'

# this is for metadata
target_begin_date = "20000101"
target_end_date = "20131231"

#this is for scraping
begin_year = 2000
end_year = 2001

# since nyt api key allows only 1000 calls for one key, so I kept three api keys on the txt file and replace it whenever it hits the limit.
# if not more than 1000 requests are needed, just put your api key
api_f = open("nytapikey.txt","r")

for line in api_f:
    api_key = line
    break;

article_total = 0


def call_the_articles(search_begin_date,search_end_date):
    url = base_url+response_format+"?q="+search_query+"&begin_date="+search_begin_date+"&end_date="+search_end_date+"&api-key="+api_key
    return json.loads(urlopen(url).read())

articles = call_the_articles(target_begin_date,target_end_date)
article_total = articles['response']['meta']['hits']


hit_f = codecs.open('article_hit.txt', 'w', encoding='utf-8')
hit_f.write("total hit : " + str(article_total) + "\n")
hit_f.close()

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

def get_monthrange(year,month):
    return monthrange(year,month)[1]

# nyt api returns only 10 articles at one time, so this part splits time period into very small chunk, and keep requestin based on the time period

def scrape_urls(begin_year,end_year,start_month,end_month,density):
    paired_data = {'start_date' : [], 'end_date':[],'hits':[], 'urls':[]}
    
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
            
                paired_data['start_date'].append(start_day)
                paired_data['end_date'].append(end_day) 
                try:
                    partial_article = call_the_articles(start_day,end_day) 
                    paired_data["hits"].append(partial_article['response']['meta']['hits'])
                
                
                    for article_num in range( int(partial_article['response']['meta']['hits']) ):
                        article_url_array = []
                        article_url_array.append(partial_article['response']['docs'][article_num]['headline']['main'])
                        paired_data["urls"].append(article_url_array)
                except:
                    print start_day + "    " + end_day
    
    return paired_data


# write all urls of articles found on the txt file

#this is for scraping
begin_year = 2006
end_year = 2004

#better to split the year not to exceed query per second limit

data_to_file = scrape_urls(begin_year,begin_year+1,1,6,10)



year_hit_total = 0

for hit_num in data_to_file["hits"]:
    year_hit_total = year_hit_total + hit_num



f = codecs.open('urls_with_hit/' + str(begin_year) +'_'+ str(year_hit_total) + '.txt', 'w', encoding='utf-8')
for urls in data_to_file["urls"]:
    for url in urls:
        f.write(url + "\n")
f.close()