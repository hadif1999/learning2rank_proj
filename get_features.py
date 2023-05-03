dclass get_features:


    def __init__(self,urls,query:str):
        import requests
        import requests
        from bs4 import BeautifulSoup
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import re
        import pickle
        import os

        self.urls = urls
        self.feats = {"url":[],"H2_lens":[] , "H3_lens":[] , "kw_in_H1":[] , "kw_in_H2":[] , "kw_in_H3":[] 
            , "kw_in_p":[] , "kw_in_anch":[] , "kw_in_foot":[] , "kw_in_url":[] , "kw_in_image_alt":[]
            ,"kw_in_meta":[] , "have_title":[] , "content_sizes_list":[] , "html_sizes":[]
         ,"download_times":[] , "link_quants":[] , "kw_in_all" : [] } # features dict
        self.Query = query
        self.soups = None


    def get_soup_obj(self , url, timeout_ =12, connect_=2, retry_= 3, backfactor = 0.5):
        import requests
        import requests
        from bs4 import BeautifulSoup
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import sys
        sys.setrecursionlimit(10000)

        session = requests.Session()
        retry = Retry(total = retry_ , connect= connect_ , backoff_factor = backfactor)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        try: 
            source= session.get(url , timeout = timeout_  )
            soup=BeautifulSoup(source.text,'html.parser')
        except: return None,None

        return soup , int(source.headers.get('content-length', 0))/1024 , len(source.content)/1024 , source.elapsed.total_seconds()



    def scrape_urls(self):
        print("\n\n\nscraping data please wait....\n\n\n")
        self.soups = [self.get_soup_obj(url) for url in self.urls]



    def get_all_features(self):

        for soup_obj,URL in zip(self.soups,self.urls):

            soup , content_size , html_size , download_time = soup_obj

            self.feats["H2_lens"].append(self.Average_tag_len('h2',soup))
            self.feats["H3_lens"].append(self.Average_tag_len('h3',soup))
            self.feats["kw_in_H1"].append(self.Calculate_tag_Keyword(self.Query ,'h1', soup ))
            self.feats["kw_in_H2"].append(self.Calculate_tag_Keyword(self.Query ,'h2', soup ))
            self.feats["kw_in_H3"].append(self.Calculate_tag_Keyword(self.Query ,'h3', soup ))
            self.feats["kw_in_p"].append(self.Calculate_tag_Keyword(self.Query ,'p', soup ))
            self.feats["kw_in_anch"].append(self.check_anch_kw(self.Query , soup)[0] )
            self.feats["link_quants"].append(self.check_anch_kw(self.Query , soup)[1])
            self.feats["kw_in_foot"].append(self.check_foot_kw(self.Query , soup) )
            self.feats["kw_in_url"].append(self.check_url_kw(self.Query , URL) )
            self.feats["kw_in_image_alt"].append(self.Calculate_alt_Keyword(self.Query , soup) )
            self.feats["kw_in_meta"].append(self.meta_kw_cal(soup) )
            self.feats["have_title"].append( "" ) # must be added
            self.feats["content_sizes_list"].append(content_size)
            self.feats["html_sizes"].append(html_size)
            self.feats["download_times"].append(download_time)
            self.feats["url"].append(URL)
            self.feats["kw_in_all"].append( self.check_all_kw(self.Query , soup)[0] )
        
        return self.feats
                    

    def Average_tag_len(self,tag,soup_str):
        tag_list=soup_str.find_all(tag)
        tag_sum=0
        tag_num= len(tag_list)
        if tag_num>0:
            for j in tag_list:
                tag_sum += len(j.text)
            return(tag_sum/tag_num)
        else:
            return 0
      

    
#Calculate the Keyword Quantity in tag    
    def Calculate_tag_Keyword(self,query,tag,soup_str):
        keywords = query.split(' ')
        tag_list=soup_str.find_all(tag)
        match_list=[]
        for keyword in keywords:
            matches = [match for match in tag_list if keyword.lower() in (match.text).lower()]
            match_list.append(len(matches))
            
        return (min(match_list))



#Checks the exsistance of Keyword in Anchor texts and number of <a>
    def check_anch_kw(self,query, soup):
        
        import re
        # Find all anchor tags in the HTML
        anchor_tags = soup.find_all('a')
        
        # If no anchor tags are found, return False
        if not anchor_tags : return False , len(anchor_tags)
        
        # Split the query string into individual words
        query_words = query.split()
        
        # Loop through all the query words and check if they appear in the anchor tags
        for word in query_words:
            found = False
            for tag in anchor_tags:
                if tag.find(string=re.compile(r'\b{}\b'.format(word))):
                    found = True
                    break
            if not found:
                return False , len(anchor_tags)
        
        # If all query words appear in the anchor tags, count the number of occurrences for each word
        counts = {}
        for word in query_words:
            occurrences = 0
            for tag in anchor_tags:
                try:
                    occurrences += len(tag.find_all(string=re.compile(r'\b{}\b'.format(word))))
                except : continue
            counts[word] = occurrences
        
        # Return the count for the word that occurred minimum
        return min(counts.values()) , len(anchor_tags)




#Checks the exsistance of Keyword in footer
    def check_foot_kw(self,query, soup):
        import re
        # Find the footer tag in the HTML
        footer_tag = soup.find('footer')
        
        # If footer tag is not found, return False
        if not footer_tag:
            return False
        
        # Split the query string into individual words
        query_words = query.split()
        
        # Loop through all the query words and check if they appear in the footer tag
        for word in query_words:
            occurrences = footer_tag.find_all(string=re.compile(r'\b{}\b'.format(word)))
            if not occurrences:
                return False
        
        # If all query words appear in the footer tag, count the number of occurrences for each word
        counts = {}
        for word in query_words:
            occurrences = footer_tag.find_all(string=re.compile(r'\b{}\b'.format(word)))
            counts[word] = len(occurrences)
        
        # Return the count for the word that occurred minimum
        return min(counts.values())


    

    
#Checks the exsistance of Keyword in URL
    def check_url_kw(self,query, url):
        # Split the query string into individual words
        query_words = query.split()
        
        # Check if all query words appear in the URL
        for word in query_words:
            if word not in url:
                return False
        
        # If all query words appear in the URL, return True
        return True



#Calculates the number of Keyword in Alt texts
    def Calculate_alt_Keyword(self,query,soup_str):
        import re
        keywords = query.split(' ')
        alt_list= re.findall('alt=".+?"',str(soup_str))
        match_list=[]
        for keyword in keywords:
            matches = [match for match in alt_list if keyword.lower() in match.lower()]
            match_list.append(len(matches))
        return(min(match_list))



#Calculates the number of meta keywords
    def meta_kw_cal(self,soup):
        # Find all the meta tags in the HTML
        meta_tags = soup.find_all('meta')
        
        # Initialize the keyword count to 0
        keyword_count = 0
        
        # Loop through all the meta tags and count the keywords
        for tag in meta_tags:

            if tag.get('name') == 'keywords':
                try:
                    keywords = tag.get('content')
                    keyword_count += len(keywords.split(','))
                except:
                    continue
        
        # Return the keyword count
        return keyword_count



# counts number of repeating of query in all page contents
    def check_all_kw(self,query, soup):
    # Find all the contents of the soup object
        contents = soup.find_all(string=True)
    
    # Join all the contents into a single string
        all_text = ''.join(contents)
    
    # Split the query string into individual words
        query_words = query.split()
    
    # Check if all query words appear in the joined text
        for word in query_words:
            if word not in all_text:
                return 0,0
    
    # If all query words appear in the joined text, count the number of occurrences
        counts = {}
        for word in query_words:
            count = all_text.count(word)
            counts[word] = count
    
    # Return the count for the word that occurred minimum
        min_count = min(counts.values())
        min_word = [k for k, v in counts.items() if v == min_count][0]
    
        return min_count, min_word
    
     