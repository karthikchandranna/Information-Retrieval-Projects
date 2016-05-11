import urllib.request
from urllib.error import URLError,HTTPError
from bs4 import BeautifulSoup
from requests import requests
from urllib.parse import urlparse, urlunparse, unquote, quote, urljoin
import httplib2
import operator
import time
import timeit
import string 
import re
import urllib.robotparser
import sys
import pickle 

 
compress = re.compile('([^/]+/\.\./?|/\./|//|/\.$|/\.\.$)')
serv_auth = re.compile('^(?:([^\@]+)\@)?([^\:]+)(?:\:(.+))?$')
deft_port = {'http': '80','https': '443','gopher': '70','news': '119','snews': '563','nntp': '119','snntp': '563','ftp': '21','telnet': '23','prospero': '191'}
rel_schemes = ['http','https','news','snews','nntp','snntp','ftp','file','']
 
 
def normalise(url,base_url):
    #get the absolute url, then taking the tuple of it and sending it t norm fn.
    #norm returns a tuple of canonicalized url, so packing it as a url and returning as a string
    return str(urlunparse(norm(urlparse(urljoin(base_url,url)))))
 
 
def norm(urltuple):
    #storing the url as a tuple 
    (scheme, authority, path, parameters, query, fragment) = urltuple
    #converting scheme to lower    
    scheme = scheme.lower()
    if authority:
        #user-information part: terminated with "@", a hostname, port number: preceded by a colon ":".
        userinfo, host, port = serv_auth.match(authority).groups()
        if host[-1] == '.':
            host = host[:-1]
        authority = host.lower()        
        if userinfo:
            #userinfo@hostname
            authority = "%s@%s" % (userinfo, authority)
        #if valid port - according to scheme
        if port and port !=deft_port.get(scheme, None):
            #userinfo@hostname:port
            authority = "%s:%s" % (authority, port)
    #checking if scheme is valid
    if scheme in rel_schemes:
        last_path = path
        #compressing mutliple '/'
        while 1:
            path =compress.sub('/', path, 1)
            if last_path == path:
                break
            last_path = path
    #encoding in utf-8
    path = unquote(path) 
    path = quote(path.encode('utf8'))
    return (scheme, authority, path, parameters, query, '')

#storing seed urls in the frontier
frontier = {}
#frontier[key]=(inlink_count,insert_time,depth)
frontier['http://en.wikipedia.org/wiki/Data_structure'] = (99999,timeit.default_timer(),1)
frontier['http://en.wikipedia.org/wiki/Associative_array'] = (99998,timeit.default_timer(),1)
frontier['http://en.wikipedia.org/wiki/Hash_table'] = (99997,timeit.default_timer(),1)
frontier['http://en.wikipedia.org/wiki/List_of_data_structures'] = (99996,timeit.default_timer(),1)
frontier['http://en.wikibooks.org/wiki/Data_Structures'] = (99995,timeit.default_timer(),1)
frontier['http://programmers.stackexchange.com/questions/tagged/data-structures'] = (99994,timeit.default_timer(),1)
frontier['http://interactivepython.org/runestone/static/pythonds/index.html'] = (99993,timeit.default_timer(),1)
frontier['http://www.quirksmode.org/js/associative.html'] = (99992,timeit.default_timer(),1)
frontier['https://msdn.microsoft.com/en-us/library/system.collections.hashtable(v=vs.110).aspx'] = (99991,timeit.default_timer(),1)
frontier['http://docs.oracle.com/javase/7/docs/api/java/util/Hashtable.html'] = (99990,timeit.default_timer(),1)

visited = []
junk_links = []
inlinks = {}
#storing seed urls in the inlinks hash
#inlink[key]=[inlink1,inlink2]
inlinks['http://en.wikipedia.org/wiki/Data_structure']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://en.wikipedia.org/wiki/Associative_array']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://en.wikipedia.org/wiki/Hash_table']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://en.wikipedia.org/wiki/List_of_data_structures']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://en.wikibooks.org/wiki/Data_Structures']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://www.w3schools.com/php/php_arrays.asp']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://interactivepython.org/runestone/static/pythonds/index.html']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://www.quirksmode.org/js/associative.html']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['https://msdn.microsoft.com/en-us/library/system.collections.hashtable(v=vs.110).aspx']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']
inlinks['http://docs.oracle.com/javase/7/docs/api/java/util/Hashtable.html']=['https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8']

def get_next_url():
    max_inlink = 0
    max_time = float("inf")
    min_depth = float("inf")
    next_url = ''
    no_inlinks = 0
    for url in frontier.keys():
        depth = frontier[url][2]
        #checking if depth of the url is < min_depth
        if depth < min_depth:
            min_depth = depth
            max_inlink = frontier[url][0]
            max_time = frontier[url][1]
            next_url = url
        #when depth is = min_depth
        elif depth == min_depth:
            no_inlinks = frontier[url][0]
            #checking if the inlinks count of the url is > max_inlink
            if no_inlinks > max_inlink:
                max_inlink = no_inlinks
                max_time = frontier[url][1]
                next_url = url
            #when inlinks count of the url = max_inlink
            elif no_inlinks == max_inlink:
                #check if url's insert time is < max_time
                if frontier[url][1] < max_time:
                    max_time = frontier[url][1]
                    next_url = url
    return next_url

count=0
while frontier and count<12000:

    #get best url
    url = get_next_url()
    print("Current page url ->  "+ url)
    parser = urlparse(url)
    rb_parse = urllib.robotparser.RobotFileParser()
    if parser.hostname is not None:        
        try:
            # read robots.txt
            rb_parse.set_url(parser.scheme+"://"+parser.hostname+"/robots.txt")
            rb_parse.read()
            time.sleep(1)
        except HTTPError as e:
            print("Status Code: "+str(e.code))
            print("Reason: "+str(e.reason))
            junk_links.append(url)
        except URLError as e:
            print("Reason: "+str(e.reason))
            junk_links.append(url)
        except:
            print("Unexpected error:"+ str(sys.exc_info()[0]))
            junk_links.append(url)
        else:
            html=''
            #checking if the url can be crawled according to robots.txt
            if rb_parse.can_fetch("*", url):  
                try:
                    # creating a response object of the url
                    response = urllib.request.urlopen(url)
                    time.sleep(1)
                except HTTPError as e:
                    print("Status Code: "+str(e.code))
                    print("Reason: "+str(e.reason))
                    junk_links.append(url)
                except URLError as e:
                    print("Reason: "+str(e.reason))
                    junk_links.append(url)
                except:
                    print("Unexpected error:"+ str(sys.exc_info()[0]))
                    junk_links.append(url)
                else:
                    #checking if the content is text/html
                    if (response is not None and response.info() is not None and response.info()["content-type"] is not None and 'text/html' in response.info()["content-type"]):
                        try:
                            #read and create a soup of the page
                            html = response.read()
                            soup = BeautifulSoup(html)
                        except:
                            print("Page ignored due to exception")
                            junk_links.append(url)
                        else:
                            #find the title of the page
                            titles = soup.find('title')
                            if titles is not None and titles.contents:
                                title = titles.contents[0]
                            else:
                                title = ''
                            #remove scripts and styles
                            for script in soup(["script", "style"]):
                                script.extract()
                            #extract text
                            text = ''
                            for texts in soup.find_all('p'):
                                text += str(texts.get_text())
                            #cleansing the text
                            lines = (line.strip() for line in text.splitlines())    
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))    
                            text = '\n'.join(chunk for chunk in chunks if chunk)

                            outlink_list = []
                            #get all links in the page
                            for link in soup.findAll('a'):
                                href=link.get('href')
                                if href is not None:
                                    try:
                                        #canonicalize the link
                                        norm_url = normalise(href,url)
                                    except:
                                        continue
                                    else:
                                        #checking if the link is new
                                        if norm_url not in frontier.keys() and  norm_url not in visited and norm_url not in junk_links:
                                            depth = frontier[url][2] + 1
                                            frontier[norm_url] = (1,timeit.default_timer(),depth)
                                        #checking if the link is in frontier, if so increment inlinks count   
                                        elif norm_url in frontier.keys():   
                                            inlink_cnt = frontier[norm_url][0]
                                            time_in_frontier = frontier[norm_url][1]
                                            depth = frontier[norm_url][2]
                                            frontier[norm_url] = (1 + inlink_cnt,time_in_frontier,depth)
                                        #update the inlinks hash for the link
                                        outlink_list.append(norm_url)
                                        if norm_url in inlinks:
                                            inlinks[norm_url].append(url)
                                        else:
                                            inlinks[norm_url] = [url]
                            #preparing the content to write to the file
                            contents = ''
                            contents += '<KCHAN_DOC>\n<KCHAN_DOCNO>'+str(url)+'</KCHAN_DOCNO>\n<KCHAN_HEADING>'+str(title)+'</KCHAN_HEADING>\n<KCHAN_HEADERS>'+str(response.info()).strip()+'</KCHAN_HEADERS>\n<KCHAN_CLEAN_FILE>'+str(text)+'</KCHAN_CLEAN_FILE>\n<KCHAN_RAW_FILE>'+str(html)+'</KCHAN_RAW_FILE>\n'
                            contents += '<KCHAN_OUTLINKS>'
                            for outlink in outlink_list:
                                contents += str(outlink)+','
                            contents = contents[:-1]
                            contents += '</KCHAN_OUTLINKS>\n</KCHAN_DOC>\n'
                            #storing the index into multiple smaller files
                            if count % 400 == 0:                                
                                file = open("C:\\Users\\hp\\Desktop\\IR_Documents\\index_file"+str(count),'a',encoding='utf-8')                                
                                current_file = "C:\\Users\\hp\\Desktop\\IR_Documents\\index_file"+str(count)
                            else:
                                file = open(current_file,'a',encoding='utf-8')

                            file.write(contents)
                            file.close()
                            visited.append(url)
                            count+=1
                    else:
                        print("Page is not text/html")
                        junk_links.append(url)
            else:
                print("Not allowed to crawl this url")
                junk_links.append(url)
    else:
        print("Invalid link")
        junk_links.append(url)
    frontier.pop(url)    
    print("Frontier:"+str(len(frontier)))
    print("visited:"+str(count))
#storing the inlinks hash                    
pickle.dump( inlinks, open( "C:\\Users\\hp\\Desktop\\IR_Documents\\Inlinks", "wb" ) )
