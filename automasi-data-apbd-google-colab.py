#@Portal Data DJPK Grabber by beta.uliansyah@pknstan.ac.id
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pytz import timezone
import sys
from requests.exceptions import ConnectionError
from google.colab import drive
drive.mount('/content/drive')

debug = True
i = 0
data_row = {}

filename = "data-apbd-2010-"+ datetime.now(timezone('Asia/Jakarta')).strftime("%Y-%m-%d--%H-%M") + ".csv"
path = F"/content/drive/My Drive/Colab Notebooks/Portal APBD/"

s = requests.Session()
r = s.get('http://www.djpk.kemenkeu.go.id/portal/data/apbd')

if r.status_code==200:
    bsoup = BeautifulSoup(r.text, 'html.parser')
    token = bsoup.find("input", {"name":"_token"})['value']
    alltahun = bsoup.find("select", {"name":"tahun"}) # print this var is essential
    print(alltahun) if debug else 0
    allprovinsi = bsoup.find("select", {"id":"sel_prov"}) # print this var is essential
    print(allprovinsi) if debug else 0

# create headers (diambil dari data APBD Nasional seluruh tahun)
for tiap_tahun in alltahun.find_all("option"): # populate all tahun
    print(tiap_tahun['value']) if debug else 0
    r = s.post('http://www.djpk.kemenkeu.go.id/portal/filter', 
                data={'_token': token, 'data': 'apbd ', 'tahun': tiap_tahun['value'], 'provinsi': '--', 'pemda': '--'}) # query nasional saja
    if "html" not in r.text and r.status_code==200:
        # create headers
        result = json.loads(r.text)
        if len(result) == 0:
            continue

        print(result) if debug else 0
        
        header_dict = {'no': '',
                      'tahun': '',
                      'pemda': '',
                      'provinsi': '' ,
                      'wilayah': '',
                      'disclaimer': '',
                      'special_row': '',
                      }

        # populate all kode akun
        for kode_postur in result['postur'].keys():
            print(kode_postur) if debug else 0
            header_dict[kode_postur+"_a"] = 0
            header_dict[kode_postur+"_r"] = 0
            header_dict[kode_postur+"_p"] = 0
            for kode_akun in result['postur'][kode_postur]['child'].keys():
                print(kode_akun) if debug else 0
                header_dict[kode_akun+"_a"] = 0
                header_dict[kode_akun+"_r"] = 0
                header_dict[kode_akun+"_p"] = 0
                for kode_subakun in result['postur'][kode_postur]['child'][kode_akun]['child'].keys():
                    print(kode_subakun) if debug else 0
                    header_dict[kode_subakun+"_a"] = 0
                    header_dict[kode_subakun+"_r"] = 0
                    header_dict[kode_subakun+"_p"] = 0
                    

# menuliskan header lengkap ke file
header_row = []
for key in header_dict.keys():
    header_row.append(key)

print("Saving to " + path + filename) if debug else 0 
with open(path+filename, mode='w', newline='') as apbdcsv_file:
    csv.writer(apbdcsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL).writerow(header_dict)
print(header_dict) if debug else 0

# Looping all tahun
data_dict = header_dict
for tiap_tahun in alltahun.find_all("option"): # populate all tahun
    print(tiap_tahun['value']) if debug else 0
    for option_provinsi in allprovinsi.find_all("option"): # populate all provinsi
    
    # sys.exit(0) if '01' in option_provinsi['value'] else 0 # stop at certain provinsi

        r = s.get('http://www.djpk.kemenkeu.go.id/portal/pemda/'+option_provinsi['value'])
        daerah = json.loads(r.text) # populate all kab/kota under provinsi

        for pemda in daerah:
            print("Populating data APBD Pemda " + daerah[pemda] + ", " + option_provinsi.text + " tahun " + tiap_tahun['value']) if debug else 0
            try:
                r = s.post('http://www.djpk.kemenkeu.go.id/portal/filter', 
                    data={'_token': token, 'data': 'apbd ', 'tahun': tiap_tahun['value'], 'provinsi': str(option_provinsi['value']), 'pemda': str(pemda)})
            except requests.exceptions.ConnectionError as e:
                pass
            except Exception as e:
                logger.error(e)
                randomtime = random.randint(1,5)
                logger.warn('ERROR - Retrying again website %s, retrying in %d secs' % (url, randomtime))
                time.sleep(randomtime)
                continue

            if "html" not in r.text and r.status_code==200 and len(json.loads(r.text)) != 0:
                i = i + 1
                print(r.text) if debug else 0
                result=json.loads(r.text)

                data_dict = {'no': i,
                            'tahun': tiap_tahun['value'],
                            'pemda': str(pemda),
                            'provinsi': str(option_provinsi['value']) ,
                            'wilayah': str(result['wilayah']),
                            'disclaimer': str(result['disclaimer']),
                            'special_row': str(result['special_row']),
                            }
                data_dict['no'] = i
                
                # iterate child
                for kode_postur in result['postur'].keys():
                    print(kode_postur) if debug else 0
                    data_dict[kode_postur+"_a"] = str(result['postur'][kode_postur]['total']['anggaran'])
                    data_dict[kode_postur+"_r"] = str(result['postur'][kode_postur]['total']['realisasi'])
                    data_dict[kode_postur+"_p"] = str(result['postur'][kode_postur]['total']['persentase'])
                    for kode_akun in result['postur'][kode_postur]['child'].keys():
                        print(kode_akun) if debug else 0
                        data_dict[kode_akun+"_a"] = str(result['postur'][kode_postur]['child'][kode_akun]['total']['anggaran'])
                        data_dict[kode_akun+"_r"] = str(result['postur'][kode_postur]['child'][kode_akun]['total']['realisasi'])
                        data_dict[kode_akun+"_p"] = str(result['postur'][kode_postur]['child'][kode_akun]['total']['persentase'])
                        for kode_subakun in result['postur'][kode_postur]['child'][kode_akun]['child'].keys():
                            print(kode_subakun) if debug else 0
                            data_dict[kode_subakun+"_a"] = pajakdaerah_a=str(result['postur'][kode_postur]['child'][kode_akun]['child'][kode_subakun]['value']['anggaran'])
                            data_dict[kode_subakun+"_r"] = pajakdaerah_a=str(result['postur'][kode_postur]['child'][kode_akun]['child'][kode_subakun]['value']['realisasi'])
                            data_dict[kode_subakun+"_p"] = pajakdaerah_a=str(result['postur'][kode_postur]['child'][kode_akun]['child'][kode_subakun]['value']['persentase'])
                
        
                # isikan result sesuai kolom
                for column_name in header_row:
                    if column_name in data_dict.keys():
                        data_row[column_name] = data_dict[column_name]
                    else:
                        data_row[column_name] = 0
                print("Isi data_row:") if debug else 0
                print(data_row) if debug else 0
                data_list = data_row.values()
                print("Saving to " + path + filename) if debug else 0 
                with open(path+filename, mode='a+', newline='') as apbdcsv_file:
                    csv.writer(apbdcsv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL).writerow(data_list)
