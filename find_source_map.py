'''
Descripttion: 
version: 
Author: 1314mylove
LastEditTime: 2021-09-14 20:28:10
'''
from sys import argv
from playwright.sync_api import sync_playwright
import requests
import getopt
import sys

js_list = []
help_info = '''
                
                                                                                             
 ###### # #    # #####      ####   ####  #    # #####   ####  ######    #    #   ##   #####  
 #      # ##   # #    #    #      #    # #    # #    # #    # #         ##  ##  #  #  #    # 
 #####  # # #  # #    #     ####  #    # #    # #    # #      #####     # ## # #    # #    # 
 #      # #  # # #    #         # #    # #    # #####  #      #         #    # ###### #####  
 #      # #   ## #    #    #    # #    # #    # #   #  #    # #         #    # #    # #      
 #      # #    # #####      ####   ####   ####  #    #  ####  ######    #    # #    # #      
                                                                                             

                [*] example: python3 find_source_map.py -u http://www.test.com\r\n\
                [*] example: python3 find_source_map.py -f domain.txt

                '''

def handle_request(request):
    req_type = request.url.split(".")[-1]
    if req_type == "js":
        js_list.append(request.url+".map")

def new_page(context,url):
    global js_list
    js_list = []
    page = context.new_page()
    page.on("request", lambda request: handle_request(request))
    try:
        page.goto(url)
    except:
        pass
    if len(js_list) > 0:
        n = 0
        for js in js_list:
            try:
                map_re = requests.get(js,timeout=10)
                if map_re.status_code == 200:
                    map_rep = map_re.text
                    if 'webpack:///' in map_rep:
                        # print(map_rep)
                        n = n+1
                        print("\033[31m[+] %s 存在sourse map 泄露\033[0m"%(url))
                        break
            except:
                break
        if n == 0:
            print("%s 不存在sourse map 泄露"%(url))
    page.close()

def run(playwright):
    url = None
    file = None
    argv = sys.argv[1:]
    if len(argv) == 0:
        print(help_info)
    try:
        opts, args = getopt.getopt(argv, "-h-f:-u:")
        for opt, arg in opts:
            if opt in ('-h','--help'):
                print(help_info)
            if opt in ['-f']:
                file = arg
            elif opt in ['-u']:
                url = arg
    except:
        print(help_info)
    chromium = playwright.chromium
    # 是否开启headless
    # browser = chromium.launch(headless=False, devtools=True)
    browser = chromium.launch()
    context = browser.new_context()
    if file != None:
        with open(file,"r") as f:
            urls = f.read().splitlines()
            for i in urls:
                new_page(context,i)
    if url != None:
        new_page(context,url)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
