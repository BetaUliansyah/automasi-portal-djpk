!pip install python-dotenv
import os
from dotenv import load_dotenv

import requests
import re
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import datetime
from pytz import timezone
import urllib3
import json
from random import randint
import time
import pandas as pd

session = None
def google_drive():
    from google.colab import drive
    drive.mount('/content/drive')
    # pajak = pd.read_csv(path+filename, error_bad_lines=False)
    
    filename = "data-tkdd-"+ datetime.now(timezone('Asia/Jakarta')).strftime("%Y-%m-%d--%H-%M") + ".csv"
    path = F"/content/drive/My Drive/Colab Notebooks/Portal APBD/"

def set_global_session():
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    
    retry_strategy = Retry(
        total=300,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    # Credits: https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

    MAX_RETRIES = 20
    global session
    if not session:
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        # adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES) # Credits: https://stackoverflow.com/questions/33895739/python-requests-module-error-cant-load-any-url-remote-end-closed-connection
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        session.verify = False

def load_env():
    load_dotenv()
    global WACHAT_APIKEY
    WACHAT_APIKEY = os.getenv('WACHAT_APIKEY')
    return True

def get_token():
    with session.get('http://www.djpk.kemenkeu.go.id/portal/data/tkdd') as response:
        if response.status_code==200 and len(response.text) != 0:
            bsoup = BeautifulSoup(response.text, 'html.parser')
            token = bsoup.find("input", {"name":"_token"})['value']
            #print("Token: " + token)
            return token

def filter_tkdd(token, tahun, provinsi, pemda):
    t0 = time.time()
    try:
        with session.post('http://www.djpk.kemenkeu.go.id/portal/filter',
            data={'_token': token, 'data': 'tkdd ', 'tahun': tahun, 'provinsi': provinsi, 'pemda': pemda}) as response:
            if response.status_code==200:
                # return (json.loads(response.text))
                return response.text
    #except requests.exceptions.ConnectionError as e:
    #    pass
    except Exception as e:
           print('It failed :(', e.__class__.__name__)
    else:
        print('It eventually worked', response.status_code)
    finally:
        t1 = time.time()
        print('Took', t1 - t0, 'seconds')
    # Credits: https://www.peterbe.com/plog/best-practice-with-retries-with-requests

def get_kodeakun_tkdd(): # return 3 list values
    print("Getting Kode Akun TKDD...")
    with session.get('http://www.djpk.kemenkeu.go.id/portal/data/tkdd') as response:
        if response.status_code==200:
            bsoup = BeautifulSoup(response.text, 'html.parser')
            token = bsoup.find("input", {"name":"_token"})['value']
            
            kodepostur_dict = {}
            kodesubpostur_dict = {}
            kodeakun_dict = {}
            koderow_dict = {}
            
            for tahun in range(2018, 2022): # populate all tahun
                print("Populating kode akun from tahun: " + str(tahun))
                result = filter_tkdd(token, tahun, "--", "--")
                json_result = json.loads(result)
                                
                # populate all kode akun
                if len(json_result) == 0:
                    continue
                for kode_postur in json_result['postur'].keys():
                    kodepostur_dict[kode_postur] = json_result['postur'][kode_postur]['text']
                    koderow_dict[kode_postur] = json_result['postur'][kode_postur]['text']
                    for kode_subpostur in json_result['postur'][kode_postur]['child'].keys():
                        kodesubpostur_dict[str(kode_postur)+str(kode_subpostur)] = json_result['postur'][kode_postur]['child'][kode_subpostur]['text']
                        koderow_dict[str(kode_postur)+str(kode_subpostur)] = json_result['postur'][kode_postur]['child'][kode_subpostur]['text']
                        for kodeakun_leaf in json_result['postur'][kode_postur]['child'][kode_subpostur]['child']:
                            kodeakun_dict[str(kode_postur)+str(kode_subpostur)+"_"+kodeakun_leaf['kodeakun']] = kodeakun_leaf['text']
                            koderow_dict[str(kode_postur)+str(kode_subpostur)+"_"+kodeakun_leaf['kodeakun']] = kodeakun_leaf['text']
            kodesubpostur_dict = dict(sorted(kodesubpostur_dict.items()))
            kodeakun_dict = dict(sorted(kodeakun_dict.items()))
            koderow_dict = dict(sorted(koderow_dict.items()))
            print("Populating kode akun completed")
            return kodepostur_dict, kodesubpostur_dict, kodeakun_dict, koderow_dict, token

def generate_header(koderows):
    print("Generating header...")
    # generate header
    header_data = ['no', 'tahun', 'kdpemda', 'nmpemda', 'kdprov', 'nmprov', 'wilayah', 'disclaimer',  'special_row' ]
    gabung_tail = list()
    for i in list(koderows.keys()):
        a = i + "_a"
        r = i + "_r"
        p = i + "_p"
        gabung_tail = gabung_tail + [a, r, p]
    header_data = header_data + gabung_tail
    return header_data
            
def parse_tkdd(json_result, kodeposturs, kodesubposturs, kodeakuns, koderows):
    print("Parsing...")
    data_dict = {}
    data_dict['wilayah'] = str(json_result['wilayah'])
    data_dict['disclaimer'] = str(json_result['disclaimer'])
    data_dict['special_row'] = json_result['special_row']

    for kodepostur in kodeposturs.keys():
        if kodepostur in json_result['postur'].keys():
            data_dict[kodepostur + "_a"] = str(json_result['postur'][str(kodepostur)]['total']['anggaran'])
            data_dict[kodepostur + "_r"] = str(json_result['postur'][kodepostur]['total']['realisasi'])
            data_dict[kodepostur + "_p"] = str(json_result['postur'][kodepostur]['total']['persentase']).replace(",",".").replace(" ","")
        for kodesubpostur in kodesubposturs:
            if kodepostur in json_result['postur'].keys() and kodesubpostur[-1:] in json_result['postur'][kodepostur]['child'].keys():
                data_dict[kodesubpostur + "_a"] = str(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['total']['anggaran'])
                data_dict[kodesubpostur + "_r"] = str(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['total']['realisasi'])
                data_dict[kodesubpostur + "_p"] = str(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['total']['persentase']).replace(",",".").replace(" ","")
            i = 0
            for kodeakun in kodeakuns:
                if kodepostur == kodeakun[:1] and kodesubpostur[-1:] == kodeakun[1:2] and kodepostur in json_result['postur'].keys() and kodesubpostur[-1:] in json_result['postur'][kodepostur]['child'].keys():
                    if i < len(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['child']) and kodeakun[-6:] in json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['child'][i]['kodeakun']:
                        data_dict[kodeakun + "_a"] = json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['child'][i]['value']['anggaran']
                        data_dict[kodeakun + "_r"] = str(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['child'][i]['value']['realisasi'])
                        data_dict[kodeakun + "_p"] = str(json_result['postur'][kodepostur]['child'][str(kodesubpostur[-1:])]['child'][i]['value']['persentase']).replace(",",".").replace(" ","")
                    
                    i = i + 1            
    return data_dict

def get_all_provinsi(): # return dict with kdprov as key, nmprov as value
    with session.get('http://www.djpk.kemenkeu.go.id/portal/data/tkdd') as response:
        if response.status_code==200:
            bsoup = BeautifulSoup(response.text, 'html.parser')
            allprovinsi = bsoup.find("select", {"id":"sel_prov"}) 
            provinsi = {}
            for option_provinsi in allprovinsi.find_all("option"): # populate all provinsi
               provinsi[option_provinsi['value']] = option_provinsi.text
            return provinsi

def get_pemdas(provinsi): # return dict with kdpemda as key, nmpemda as value
    with session.get('http://www.djpk.kemenkeu.go.id/portal/pemda/' + provinsi) as response:
        if response.status_code==200 and len(response.text) != 0:
            pemdas = json.loads(response.text)
            return pemdas

def wachat_send_message(tujuan, pesan, sender, apikey='F0C584900AB90E1040862FC0B43F561E'):
    HEADERS = {"Accept": "application/json", "APIKey": apikey }
    PAYLOADS = {'destination': tujuan, 'sender': sender, 'message': pesan}

    with session.post(
        'https://api.wachat-api.com/wachat_api/1.0/message',
        headers=HEADERS,
        json=PAYLOADS,
        # Skip SSL Verification
        # verify=False
    ) as response:
        if response.status_code==200:
            #print("Status code: " + str(r.status_code))
            #print("Response: " + r.text)
            return True
          
if __name__ == "__main__":
    set_global_session()
    load_env()
    start_time = datetime.datetime.now(timezone('Asia/Jakarta'))
    print("Start script at: " + datetime.datetime.now(timezone('Asia/Jakarta')).strftime("%-d-%m-%Y") + " at " + str(start_time))
    
    kodeposturs, kodesubposturs, kodeakuns, koderows, token = get_kodeakun_tkdd()

    # generate header
    header_data = generate_header(koderows)
    # generate prov
    allprovinsi = get_all_provinsi()
    
    datadf = pd.DataFrame(columns = header_data)
    print("Are you executing this?")
    for tahun in range(2018, 2022):
        print("Executing tahun: ", tahun)
        for kdprov, nmprov in allprovinsi.items():
            print("Executing provinsi loop: ", kdprov, nmprov)
            for kdpemda, nmpemda in get_pemdas(kdprov).items():    
                print("Executing pemda loop: ", tahun, kdpemda, nmpemda)
                result_dict = {}
                pemda_result = filter_tkdd(token, tahun, kdprov, kdpemda)
                if pemda_result is None:
                    continue
                json_result = json.loads(pemda_result)
                result_dict = parse_tkdd(json_result, kodeposturs, kodesubposturs, kodeakuns, koderows)
                result_dict['tahun'] = tahun
                result_dict['kdpemda'] = kdpemda
                result_dict['nmpemda'] = nmpemda
                result_dict['kdprov'] = kdprov
                result_dict['nmprov'] = nmprov
                print("Get data tahun", tahun, "prov", nmprov, "pemda", nmpemda)
                print(result_dict)
                datadf = datadf.append(result_dict, ignore_index = True)
                filename = "data-tkdd-"+ datetime.datetime.now(timezone('Asia/Jakarta')).strftime("%Y-%m-%d--%H-%M") + ".csv"
                datadf.to_csv(filename)
        pesan = 'Get data TKDD tahun ' + str(tahun) + ' sudah selesai'
        wachat_send_message('628567074554', pesan, '6282189096866', apikey='F0C584900AB90E1040862FC0B43F561E')
    print("datadf:")
    print(datadf)
    filename = "data-tkdd-"+ datetime.datetime.now(timezone('Asia/Jakarta')).strftime("%Y-%m-%d--%H-%M") + ".csv"
    datadf.to_csv(filename)

    duration = datetime.datetime.now(timezone('Asia/Jakarta')) - start_time
    print("Duration: " + str(duration))                      
