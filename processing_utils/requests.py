import requests
import yaml

def get_DataSources():
    file = open('settings.yaml')
    setttingsFile = yaml.safe_load(file)
    requestHeaders = {
        "apikey": setttingsFile['chemSpyderApikey'],
        "Accept": "application/json",
    }
    requestUrl = "https://api.rsc.org/compounds/v1/lookups/datasources"
    response = exceptGetRequest(requestUrl, requestHeaders)
    if (response != "Timeout") & (response.status_code == requests.codes["ok"]):
        return response.json()["dataSources"]
    else:
        return response
        

def get_ChemSpyederDatas_For_Features(fetures: list, dataSources: list, charge = -1,progress_callback=None):
    for i in range(int((len(fetures) / 100)) + 1):
        feturesCutted = list()
        for k in range(i * 100, (i * 100) + 100):
            feturesCutted.append(fetures[k])
            if progress_callback is not None:
                progress_callback.emit(int((k + 1) / (len(fetures)) * 50))
            if k == len(fetures) - 1:
                break
        get_Feature_Ids_request(feturesCutted, dataSources, charge)
    get_Feature_Formulas_Request(fetures, progress_callback)

def get_Feature_Ids_request(fetures: list, dataSources: list, charge = -1):
    if len(fetures) < 1:
        return
    file = open('settings.yaml')
    setttingsFile = yaml.safe_load(file)
    requestHeaders = {
        "apikey": setttingsFile['chemSpyderApikey'],
        "Accept": "application/json",
        "Content-Type": "application/json"
        }
    idsRequestUrl = "https://api.rsc.org/compounds/v1/filter/mass/batch"
    searchingStruct = {
        "featureToSearch" : list(),
        "idsRequestBody" : {
            "masses": list(),
            "dataSources": list()
            }
    }

    for feature in fetures:
        if len(feature.chemSpyder_mz_Results) == 0:
            searchingStruct["featureToSearch"].append(feature)
            mass = {
                "mass": feature.mz + charge,
                "range": feature.delta_mz
                }
            searchingStruct["idsRequestBody"]["masses"].append(mass)

    if len(searchingStruct["idsRequestBody"]["masses"]) == 0:
        return
    
    searchingStruct["idsRequestBody"]["dataSources"] = dataSources

    response = exceptPostRequest(idsRequestUrl, requestHeaders, searchingStruct["idsRequestBody"])

    if (response == "Timeout") | (response.status_code != requests.codes["ok"]):
        return

    queryId = response.json()["queryId"]

    requestUrl = "https://api.rsc.org/compounds/v1/filter/mass/batch/" + queryId + "/results"

    response = exceptGetRequest(requestUrl, requestHeaders)

    if (response == "Timeout") | (response.status_code != requests.codes["ok"]):
        return

    array = response.json()["batchResults"]

    for i in range(len(searchingStruct["featureToSearch"])):
        searchingStruct["featureToSearch"][i].chemSpyder_mz_Results.clear()
        for result in array[i]["results"]:
             if searchingStruct["featureToSearch"][i].chemSpyder_mz_Results.get(result["id"]) == None:
                searchingStruct["featureToSearch"][i].chemSpyder_mz_Results[result["id"]] = {
                 "id" : result["id"],
                 "CommonName": "",
                 "Formula": ""
                 }

def get_Feature_Formulas_Request(fetures: list, progress_callback=None):
    file = open('settings.yaml')
    setttingsFile = yaml.safe_load(file)
    requestHeaders = {
        "apikey": setttingsFile['chemSpyderApikey'],
        "Accept": "application/json",
        "Content-Type": "application/json"
        }
    requestUrl = "https://api.rsc.org/compounds/v1/records/batch"
    recordIds = list()
    records = dict()

    for feature in fetures:
        for id in  feature.chemSpyder_mz_Results:
            if feature.chemSpyder_mz_Results[id]["Formula"] == "":
                recordIds.append(id)

    if len(recordIds) == 0:
         return
    
    for i in range(int((len(recordIds) / 100)) + 1):
        recordsIdsCutted = list()
        for k in range(i * 100 , (i * 100) + 100):
            recordsIdsCutted.append(recordIds[k])
            if progress_callback is not None:
                progress_callback.emit(int(((k + 1) / (len(recordIds)) * 50) + 50))
            if k == len(recordIds) - 1:
                break
        requestBody = {
                "recordIds": recordsIdsCutted,
                "fields": [
                "Formula",
                "commonName"
                    ]
                }
        response = exceptPostRequest(requestUrl, requestHeaders, requestBody)
        if (response == "Timeout") | (response.status_code != requests.codes["ok"]):
            return
        for record in response.json()["records"]:
            records[record["id"]] = {
                "commonName": record["commonName"], 
                "formula": record["formula"]
                }
    
    for feature in fetures:
        for id in  feature.chemSpyder_mz_Results:
            feature.chemSpyder_mz_Results[id]["CommonName"] = records[id]["commonName"]
            feature.chemSpyder_mz_Results[id]["Formula"] = records[id]["formula"]
    
def exceptGetRequest(requestUrl, requestHeaders):
    for i in range(10):
        try:
            response = requests.get(
                requestUrl, headers=requestHeaders, timeout=1)
            return response
        except requests.Timeout:
            if i == 9:
                return "Timeout"
            continue

def exceptPostRequest(requestUrl, requestHeaders, requestBody):
    for i in range(10):
        try:
            response = requests.post(
                requestUrl, headers=requestHeaders, json=requestBody, timeout=3)
            return response
        except requests.Timeout:
            if i == 9:
                return "Timeout"
            continue
