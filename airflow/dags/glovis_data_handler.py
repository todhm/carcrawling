from bs4 import BeautifulSoup
from crawl_utils import get_session_soup_data
from string_utils import parse_number
import requests 
from urllib.parse import urlsplit, parse_qs
import re 
import os 


class GlovisDataHandler(object):

    def __init__(self):
        with requests.Session() as s:
            data={}
            data['id'] = os.environ.get("GLOVIS_ID")
            data['idsaveyn'] = 'N'
            data['passno'] = os.environ.get("GLOVIS_PASSWORDS")
            data['returnUrl'] = ''
            login_req = s.post('https://www.glovisaa.com/loginProc.do', data=data)
            self.session = s


    def get_last_page(self,loc='sihwa'):
        result_dict = {}
        if loc =='bundang':
            url = 'https://www.glovisaa.com/memcompany/memAuctionList.do?rc=FTsAppxQe9xulZt5Dvimrg%3D%3D'
        elif loc =='yangsan':
            url = 'https://www.glovisaa.com/memcompany/memAuctionList.do?rc=CchONTK9tj7p26%2BAyvF%2F3Q%3D%3D'
        else:
            url = 'https://www.glovisaa.com/memcompany/memAuctionList.do?rc=oEvA4%2F%2FTX1wMbwtpyaL9Fw%3D%3D'
        soup = get_session_soup_data(self.session,url)
        div_tag = soup.find("div",attrs={"class":"paging"})
        if not div_tag:
            return False
        last_page_tag = div_tag.find("a",attrs={'class':"last"},recursive=False)
        if not last_page_tag:
            return False 
        page_string = last_page_tag['href']
        query = urlsplit(page_string).query
        params = parse_qs(query)
        last_page_lst = params['page']
        if not last_page_lst:
            return False 
        last_page = int(last_page_lst[0])
        result_dict['last_page'] = last_page
        board_div = soup.find('div',attrs={"class":'boarddv'})
        if not board_div:
            return False

        ul_div = board_div.find("ul",attrs={"class":"lnelist"})
        if not ul_div:
            return False
        li_list = ul_div.findAll("li")
        if not li_list:
            return False 
        first_li = li_list[0]

        car_id_mother_div = first_li.find("div",attrs={"class":"txt"})
        if car_id_mother_div:
            car_id_div = car_id_mother_div.find('div',recursive=False)
            car_ids_list = car_id_div.findAll("span",attrs={"class":"n"})
            if car_ids_list:
                result_dict['auction_number'] = int(car_ids_list[0].text)
            else:
                return False 
        else:
            return False 
        

        car_loc_span = first_li.find("span",attrs={"class":"stk"})
        if car_loc_span:
            car_loc_span_img = car_loc_span.find("img")
            if car_loc_span_img:
                result_dict['auction_loc'] = car_loc_span_img['title']
            else:
                return False 
        else:
            return False 
                

        return result_dict

    def parse_page_list(self,loc,last_page):
        if loc =='bundang':
            url_list =[{'site':f'https://www.glovisaa.com/memcompany/memAuctionList.do?&ac=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&acc=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&rc=FTsAppxQe9xulZt5Dvimrg%3D%3D&atn=MpjHSVioPPhzY0HvPXEF6Q%3D%3D&page1=1&page={i}'}
             for i in range(1,last_page+1)]
        elif loc =='yangsan':
            url_list =[
                {'site':
                f'https://www.glovisaa.com/memcompany/memAuctionList.do?&ac=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&acc=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&rc=CchONTK9tj7p26%2BAyvF%2F3Q%3D%3D&atn=iWx1JiPSS1r4j2K5%2BPNwGQ%3D%3D&page1=1&page={i}'}
             for i in range(1,last_page+1)]
        else:
            url_list =[
            {'site':f'https://www.glovisaa.com/memcompany/memAuctionList.do?&ac=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&acc=TQhYt3GD6GvgPdVw1QX%2BWg%3D%3D&rc=oEvA4%2F%2FTX1wMbwtpyaL9Fw%3D%3D&atn=iWx1JiPSS1r4j2K5%2BPNwGQ%3D%3D&page1=1&page={i}'}
            for i in range(1,last_page+1)]
        return url_list



    def get_car_page_data(self,page):
        soup = get_session_soup_data(self.session,page)
        board_div = soup.find('div',attrs={"class":'boarddv'})
        if not board_div:
            return False
        ul_div = board_div.find("ul",attrs={"class":"lnelist"})
        li_list = ul_div.findAll("li")
        car_data_dict_list = []
        for li in li_list:
            car_data_dict = self.parse_car_data_dict(li)
            if car_data_dict:
                car_data_dict_list.append(car_data_dict)

        return car_data_dict_list

        


    def parse_car_data_dict(self,first_li):
        car_data_dict ={
            'car_brand':None,
            'auction_id':None,
            'car_name':None,
            'year':None, 
            'transmission':None, 
            'fuel_type':None,
            'engine_size':None, 
            'kilos':None, 
            'car_color':None, 
            'car_img_src':None, 
            'car_loc':None, 
            'auction_car_id':None, 
            'car_type':None, 
            'car_owner':None, 
            'car_reputation':None, 
            'car_auction_start_price':None
        }

        car_id_mother_div = first_li.find("div",attrs={"class":"txt"})
        if car_id_mother_div:
            car_id_div = car_id_mother_div.find('div',recursive=False)
            car_ids_list = car_id_div.findAll("span",attrs={"class":"n"})
            if car_ids_list:
                car_data_dict['auction_id'] = int(car_ids_list[0].text)
                car_data_dict['auction_car_id'] = int(car_ids_list[1].text)
            else:
                return False 
        else:
            return False
    

            
        car_name_span = first_li.find("div",attrs={"class":"ti"})
        if car_name_span:
            car_string = car_name_span.text.strip()
            car_brand_re = re.match('\[.+\]',car_string)
            if car_brand_re:
                car_brand = car_brand_re.group()
                car_data_dict['car_name'] = car_string.replace(car_brand,'').strip()
                car_data_dict['car_brand']  = car_brand.replace("[",'').replace(']','')
            else:
                return False 
        else:
            return False 


        car_img = first_li.find("div",attrs={"class":"thumn"}).find('img')
        car_data_dict['car_img_src'] = car_img['src']

        car_loc_span = first_li.find("span",attrs={"class":"stk"})
        if car_loc_span:
            car_loc_span_img = car_loc_span.find("img")
            if car_loc_span_img:
                car_data_dict['car_loc'] = car_loc_span_img['title']
                
            
        info_list = [ x.text.strip() for x in first_li.findAll("span",attrs={"class":"sp4"})]
        for i,x in enumerate(info_list):
            if i == 0:
                car_data_dict['year']=int(x)
            elif i == 1:
                car_data_dict['transmission'] = x
            elif i == 2:
                car_data_dict['fuel_type'] = x
            elif i == 3:
                car_data_dict['engine_size'] = parse_number(x)
            elif i == 4:
                car_data_dict['kilos'] = parse_number(x)
            elif i == 5:
                car_data_dict['car_color'] = x
                
        first_li.findAll("span",attrs={"class":"sp4"})

        car_state_div = first_li.find("div",attrs={"class":"spright"})
        if car_state_div:
            car_state_list = car_state_div.findAll("span",attrs={"class":"sp"})
            car_state_list = [ x.text for x in  car_state_list]
            for i,x in enumerate(car_state_list):
                if i == 0:
                    car_data_dict['car_type'] = x.strip()
                if i == 1:
                    car_data_dict['car_owner'] = x.strip()
                if i == 2:
                    car_data_dict['car_reputation'] = x.strip()
                if i == 3:
                    car_data_dict['car_auction_start_price'] = parse_number(x)*10000 if '만원' in x else parse_number(x)

        return car_data_dict


        

    def close(self):
        self.session.get('https://www.glovisaa.com/logout.do')
        self.session.close()





