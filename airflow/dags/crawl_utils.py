import requests 
from bs4 import BeautifulSoup


def get_login_session():
    with requests.Session() as s:
        data={}
        data['id'] = '7637'
        data['idsaveyn'] = 'N'
        data['passno'] = 'dGltZTM4MjIlNDA='
        data['returnUrl'] = ''
        login_req = s.post('https://www.glovisaa.com/loginProc.do', data=data)
        return s


def get_session_soup_data(s,url):
    response = s.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text)
        return soup 
    else:
        return None 


