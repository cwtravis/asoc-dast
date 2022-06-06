import requests
import time
import os

key_id = os.getenv('ASOC_KEY_ID')
key_sec = os.getenv('ASOC_KEY_SEC')
app_id = os.getenv('ASOC_APP_ID')

def get_scan_status(auth_token, scan_id):
    headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }
    r = requests.get(f"https://cloud.appscan.com/api/v2/Scans/{scan_id}", headers=headers)
    if r.status_code != 200:
        print(f"Error getting scan status: {r.status_code}")
        return None
    return r.json()

def run_scan():
    
    data = {
        "KeyId": key_id,
        "KeySecret": key_sec
    }
    r = requests.post("https://cloud.appscan.com/api/V2/Account/ApiKeyLogin", json=data)
    
    token = None
    
    if r.status_code != 200:
        print("Error logging into ASoC")
        return
        
    token = r.json()["Token"]
    print("Auth successful to ASoC")
    print("Starting DAST Scan")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "ScanType": "Staging",
        "StartingUrl": "http://demo.testfire.net?mode=demo",
        "LoginUser": "jsmith",
        "LoginPassword": "demo1234",
        "ScanName": "Concourse_DAST_SCAN",
        "AppId": app_id
    }
    
    r = requests.post("https://cloud.appscan.com/api/v2/Scans/DynamicAnalyzer", headers=headers, json=data)
    
    if r.status_code > 201:
        print("Error creating scan")
        return
    
    scan_id = r.json()["Id"]
    print(f"Created Scan {scan_id}")
    
    print(f"Waiting for scan to finish")
    start = time.time()
    elapsed = 0
    max = 60 * 30
    prev_status = ""
    while elapsed < max:
        status_obj = get_scan_status(token, scan_id)
        if status_obj is None:
            print("Error getting status")
        status = status_obj["LatestExecution"]["ExecutionProgress"]
        if status != prev_status:
            prev_status = status
            print(f"Scan Status: {prev_status}")
        #Pending, Running, UnderReview, RunningManually, Paused, Completed
        if status == "ERROR" or status == "Completed":
            print(f"Scan completed with status: {status}")
            print("Scan Summary:")
            print(f"\t High Issues: {status_obj['LatestExecution']['NHighIssues']}")
            print(f"\t Med Issues: {status_obj['LatestExecution']['NMediumIssues']}")
            print(f"\t Low Issues: {status_obj['LatestExecution']['NLowIssues']}")
            print()
            print("For full details visit:")
            print(f"https://cloud.appscan.com/main/myapps/{app_id}/scans/{scan_id}/scanOverview")
            break
        time.sleep(30)
        
  
    
run_scan()
