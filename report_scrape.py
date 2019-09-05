# https://analytics.google.com/analytics/web/#/report/content-pages/a2709703w5019332p5171938/explorer-segmentExplorer.segmentId=analytics.pageTitle&explorer-table.plotKeys=%5B%5D&explorer-table.advFilter=%5B%5B0,%22analytics.pageTitle%22,%22EQ%22,%22iowastatedaily.com%20%7C%20We%20deliver.%20You%20discover.%22,1%5D,%5B0,%22analytics.pageTitle%22,%22EQ%22,%22News%20%7C%20iowastatedaily.com%22,1%5D,%5B0,%22analytics.pageTitle%22,%22EQ%22,%22Sports%20%7C%20iowastatedaily.com%22,1%5D,%5B0,%22analytics.pageTitle%22,%22EQ%22,%22Opinion%20%7C%20iowastatedaily.com%22,1%5D,%5B0,%22analytics.pageTitle%22,%22EQ%22,%22(not%20set)%22,1%5D,%5B0,%22analytics.pageTitle%22,%22EQ%22,%22User%20%7C%20iowastatedaily.com%22,1%5D,%5B0,%22analytics.pageTitle%22,%22PT%22,%22Search%20%7C%20iowastatedaily.com%22,1%5D,%5B0,%22analytics.pageTitle%22,%22PT%22,%22Men's%20Basketball%20%7C%20iowastatedaily.com%22,1%5D%5D&explorer-table.rowCount=50
# 
# https://analytics.google.com/analytics/web/#/report/content-pages/a2709703w5019332p5171938/_u.date00=20190818&_u.date01=20190824&explorer-table.advFilter=%5B%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2F%22,1%5D,%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2Fsports~2F%22,1%5D,%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2Fnews~2F%22,1%5D,%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2Fsports~2Ffootball~2F%22,1%5D,%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2Fopinion~2F%22,1%5D,%5B0,%22analytics.pagePath%22,%22EQ%22,%22~2Fsports~2Fmens_basketball~2F%22,1%5D%5D&explorer-table.plotKeys=%5B%5D&explorer-table.rowCount=50/

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm
import time
import sys, getopt

def mkNewReport(inputfile):
    df=pd.read_csv(inputfile)
    Page=df['Page']
    StoryTitle=[]
    Authors=[]
    Pageviews=df['Pageviews']
    UniquePageviews=df['Unique Pageviews']
    AvgTimeOn=df['Avg. Time on Page']
    Entrances=df['Entrances']
    Bounce=df['Bounce Rate']
    Exit=df['% Exit']

    #Loop to add Authors, urls, and StoryTitle arrays to df
    Authors=[]
    urls=[]
    StoryTitle=[]
    count=0
    for page in tqdm(Page):
        u="http://www.iowastatedaily.com"+df['Page'][count]
        urls.append(u)
        url="http://www.iowastatedaily.com/"+df['Page'][count]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        if not soup.find_all(itemprop='author'):
            t = soup.find_all(class_='tnt-byline')[0].get_text()
        else:
            t = soup.find_all(itemprop='author')[0].get_text()
        a=t.find('\n')
        b=t.find(',')
        c=[a,b]
        if 'By'!=t[0:2] and 'by'!=t[0:2]:
            if c != [-1,-1]:
                k=min(i for i in c if i > 0)
                t=t[:k]
            else:
                t=t
        else:
            if c != [-1,-1]:
                k=min(i for i in c if i > 0)
                t=t[3:k]
            else:
                t=t[3:]
        Authors.append(t)
        soup = BeautifulSoup(page.content, 'html.parser')
        if not soup.find_all(class_='headline'):
            t = ""
        else:
            t = soup.find_all(class_='headline')[0].get_text()
        t=" ".join(t.split())
        StoryTitle.append(t)
        count = count + 1

    #Make new report
    newReport = pd.DataFrame({
        "URL":urls,
        "Page Title": StoryTitle,
        "Author": Authors,
        "Page Views": Pageviews,
        "Unique Pageviews": UniquePageviews,
        "Average Time on Page":AvgTimeOn,
        "Entrances":Entrances,
        "Bounce Rate":Bounce,
        "Exit Rate":Exit
    })
    #newReport.loc[len(newReport)] = ["","","TOTALS",df[Pageviews].mean(),df[UniquePageviews].mean(),df[AvgTimeOn].mean(),df[Entrances].mean(),df[Bounce].mean(),df[Exit].mean()]
    return newReport

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('report_scrape.py -i <inputfile>.csv -o <outputfile>.xlsx')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('report_scrape.py -i <inputfile>.csv -o <outputfile>.xlsx')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   writer = pd.ExcelWriter(outputfile, engine='xlsxwriter',options={'strings_to_urls': False})
   mkNewReport(inputfile).to_excel(writer)
   writer.close()


if __name__ == "__main__":
   main(sys.argv[1:])