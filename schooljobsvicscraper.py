# Copyright 2025 schooljobsvicscraper authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import glob
import html
import os
import re
import requests
import tomli
import urllib3

from lxml import etree
import pandas as pd

urllib3.disable_warnings()

regions = ['North-Eastern Victoria Region',
           'North-Western Victoria Region',
           'South-Western Victoria Region',
           'South-Eastern Victoria Region']

def get_icsid(r: str) -> str:
     # extract ICSID 
    pattern = "id='ICSID' value='(?P<icsid>.*?)'"
    m = re.search(pattern, r.text)
    icsid = m.group('icsid')
    return icsid

def get_statenum(r: str) -> str:
    # get current statenum
    pattern = "id='ICStateNum' value='(?P<statenum>[0-9]*?)'"
    m = re.search(pattern, r.text)
    statenum = m.group('statenum')
    return statenum

def get_statenum_after_action(r: str) -> str:
    pattern = "ICStateNum\\.value=(?P<statenum>[0-9]*?);"
    m = re.search(pattern, r.text)
    statenum = m.group('statenum')
    return statenum

def sort_by_date_payload(icsid, statenum):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"HRS_AGNT_RSLT_I$srt17$0",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICChart":'{ "aChHDP": [], "aChTp": [],"aChPTF": [] }',
           "PTS_FCTCHT_DATA":"",
           "PTS_TREEFACETCHG":"",
           "ICAppClsData":"",
           "win0hdrdivPT_SYSACT_HELP":"psc_hidden"
          }

def select_region_payload(icsid, statenum, select_id):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":f"PTS_SELECT${select_id}",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICChart":'{ "aChHDP": [], "aChTp": [],"aChPTF": [] }',
           "PTS_FCTCHT_DATA":"",
           "PTS_TREEFACETCHG":"",
           "ICAppClsData":"",
            f"PTS_SELECT$chk${select_id}":"Y",
            f"PTS_SELECT${select_id}":"Y"
          }

def get_first_job_payload(icsid, statenum, select_id):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"HRS_VIEW_DETAILS$0",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICChart":'{ "aChHDP": [], "aChTp": [],"aChPTF": [] }',
           "PTS_FCTCHT_DATA":"",
           "PTS_TREEFACETCHG":"",
           "ICAppClsData":"",
           f"PTS_SELECT$chk${select_id}":"N",
           "win0divPTS_FCTVALUES_GB$5":""
          }

def get_subject_duties_payload(icsid, statenum):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"DOE_JO_WRF_JPM_DESCR90",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICAppClsData":"",
          }

def close_subject_duties_payload(icsid, statenum):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"#ICCancel",
           "ICModelCancel":1,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICAppClsData":"",
          }

def get_next_job_payload(icsid: str, statenum: str) -> dict:
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"DERIVED_HRS_FLU_HRS_NEXT_PB",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICAppClsData":"",
          }

def get_next_provisional_appointments_payload(icsid, statenum):
    return {"ICAJAX":1,
           "ICNAVTYPEDROPDOWN": 0,
           "ICType":"Panel",
           "ICElementNum":0,
           "ICStateNum":statenum,
           "ICAction":"DET_HRS_PROV_AP$hdown$0",
           "ICModelCancel":0,
           "ICXPos":0,
           "ICYPos":0,
           "ResponsetoDiffFrame":-1,
           "TargetFrameName":"None",
           "FacetPath":"None",
           "ICFocus":"",
           "ICSaveWarningFilter":0,
           "ICChanged":0,
           "ICSkipPending":0,
           "ICAutoSave":0,
           "ICResubmit":0,
           "ICSID":icsid,
           "ICActionPrompt":"false",
           "ICTypeAheadID":"",
           "ICBcDomData":"UnknownValue",
           "ICDNDSrc":"",
           "ICPanelHelpUrl":"",
           "ICPanelName":"",
           "ICPanelControlStyle":"",
           "ICFind":"",
           "ICAddCount":"",
           "ICAppClsData":"",
          }

def download_jobs(output_dir:str, max_jobs_per_region:int = 300, found_in_last_run_limit:int = 40):
    s = requests.Session()

    jobs_files = glob.glob(f"{output_dir}/recruitment online jobs [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.csv")
    last_run_job_ids = []
    for i in range(-1,-14,-1):
        last_run_job_ids += list(pd.read_csv(jobs_files[i]).drop_duplicates(subset="jobid")['jobid'].values)

    records = []

    for region in regions:
        # open jobs page
        url = "https://edupay.eduweb.vic.gov.au/psc/EDUPPRD1_EA/APPLICANT/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&Action=U"
        r = s.get(url, verify=False)

        icsid = get_icsid(r)
        statenum = get_statenum(r)

        # sort by date posted, twice to get newest to oldest
        payload = sort_by_date_payload(icsid, statenum)
        url = "https://edupay.eduweb.vic.gov.au/psc/EDUPPRD1_EA/APPLICANT/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL"
        r = s.post(url, data=payload)
        statenum = get_statenum_after_action(r)
        payload = sort_by_date_payload(icsid, statenum)
        r = s.post(url, data=payload)
        statenum = get_statenum_after_action(r)
        
        # filter for region
        tree   = etree.fromstring(r.content)
        es = tree.xpath(f".//FIELD[contains(text(),'{region}')]")
        select_id = es[0].attrib['id'][18:]
        payload = select_region_payload(icsid, statenum, select_id)
        r = s.post(url, data=payload)
        statenum = get_statenum_after_action(r)

        # open first job
        payload = get_first_job_payload(icsid, statenum, select_id)
        r = s.post(url, data=payload)
        statenum = get_statenum(r)

        prev_found = 0
        new_found_after_prev_found = 0
        for i in range(max_jobs_per_region):
            # get job details
            pattern="id='HRS_SCH_WRK2_POSTING_TITLE' >(?P<jobtitle>.*?)</span>.*?id='HRS_SCH_WRK2_HRS_JOB_OPENING_ID' >(?P<jobid>[0-9]*?)</span>.*?id='HRS_SCH_WRK_HRS_DESCRLONG' >(?P<location>.*?)</span>.*?id='DERIVED_ER_DOE_DESCR\\$191\\$' >(?P<department>.*?)</span>.*?id='DOE_JO_WRF_DESCRLONG' >(?P<roletype>.*?)</span>.*?id='HRS_SCH_WRK_HRS_FULL_PART_TIME\\$75\\$' >(?P<fullorparttime>.*?)</span>.*?id='HRS_SCH_WRK_HRS_REG_TEMP\\$76\\$' >(?P<ongoingorfixedterm>.*?)</span>.*?id='HRS_JOBCODE_I_DESCR' >(?P<classification>.*?)</span>.*?id='DERIVED_ER_DOE_HRS_JO_PST_CLS_DT' >(?P<applyby>.*?)</span>.*?id='HRS_WRK2_BEGIN_DT' >(?P<begindate>.*?)</span>.*?id='HRS_WRK2_END_DT' >(?P<enddate>.*?)</span>.*?id='HRS_WRK2_STD_HOURS' >(?P<hours>.*?)</span>.*?id='DERIVED_ER_DOE_CONTACT_NAME' >(?P<contactname>.*?)</span>.*?id='DERIVED_ER_DOE_CONTACTPHONENBR' >(?P<phone>.*?)</span>.*?id='DERIVED_ER_DOE_CONTACTURL' >(?P<schoolwebsite>.*?)</span>"
            m = re.search(pattern, r.text, flags=re.DOTALL)
            if not m:
                break
            record = {}
            fields = ["jobtitle", "jobid", "location", "department", "roletype", 
                    "fullorparttime", "ongoingorfixedterm", "classification", "applyby",
                    "begindate", "enddate", "hours", "contactname", "phone", "schoolwebsite"]
            for field in fields:
                record[field] = html.unescape(m[field])
            
            if int(record['jobid']) in last_run_job_ids:
                prev_found += 1
            elif prev_found > 0:
                new_found_after_prev_found += 1
            if prev_found >= found_in_last_run_limit:
                break
            
            # get Subjects/Duties if listed
            pattern = "DOE_JO_WRF_JPM_DESCR90"
            m = re.search(pattern, r.text)
            if m:
                # open subjects/duties
                payload = get_subject_duties_payload(icsid, statenum)
                r = s.post(url, data=payload)
                statenum = get_statenum(r)

                # subjects/duties row pattern
                pattern = """<tr.*?id='DOE_SUBJDUTY_VW_JPM_DESCR90\\$[0-9]*' >(?P<subjectduty>.*?)</span>.*?id='DOE_SUBJDUTY_VW_JPM_PROMPT_3\\$[0-9]*' >(?P<level>.*?)</span>.*?</tr>"""
                ms = re.findall(pattern,r.text, flags=re.DOTALL)
                subjectduties = [{"subjectduty":subjectduty, "level":level} for subjectduty,level in ms]
                record["subjectduties"] = subjectduties

                
                # close subject duties
                # get current statenum
                payload = close_subject_duties_payload(icsid, statenum)
                r = s.post(url, data=payload)
                statenum = get_statenum_after_action(r)        
            
            records.append(record)

            # open next job
            payload = get_next_job_payload(icsid, statenum)
            r = s.post(url, data=payload)
            try:
                statenum = get_statenum(r)
            except AttributeError:
                break
        now = datetime.datetime.today().strftime("%Y-%m-%d %H%M%S")
        print(f"{now} {region} {i-prev_found} new jobs found.")
        
    now = datetime.datetime.today().strftime("%Y-%m-%d %H%M%S")
    df = pd.DataFrame.from_records(records)
    df.to_csv(f"{output_dir}/recruitment online jobs {now}.csv")


def download_provisional_appointments(output_dir:str):
    s = requests.Session()
    records = []

    url = "https://edupay.eduweb.vic.gov.au/psc/EDUPPRD1_EA/APPLICANT/HRMS/c/DOE_MENU_HRS.DOE_HRS_PROV_APPNT.GBL?Page=DOE_HRS_PROV_APPNT"
    prov_appointments_pattern = "id='DOE_HRS_PROV_AP_HRS_JOB_OPENING_ID\\$[0-9]*' >(?P<jobid>[0-9]*)</span>.*?id='DOE_HRS_PROV_AP_SCHOOL\\$[0-9]*' >(?P<school>.*?)</span>.*?id='DOE_HRS_PROV_AP_HRS_PRM_PST_TITLE\\$[0-9]*' >(?P<jobtitle>.*?)</span>.*?id='DOE_HRS_PROV_AP_JOBCODE\\$[0-9]*' >(?P<jobclass>.*?)</span>.*?id='DOE_HRS_PROV_AP_NAME_DISPLAY\\$[0-9]*' >(?P<applicant>.*?)</span>.*?id='DOE_HRS_PROV_AP_CLOSE_DT\\$[0-9]*' >(?P<grievanceclosedate>.*?)</span>"

    r = s.get(url)
    icsid = get_icsid(r)
    statenum = get_statenum(r)

    ms = re.findall(prov_appointments_pattern, r.text, flags=re.DOTALL)
    for m in ms:
        fields = ["jobid", "school", "jobtitle", "jobclass", "applicant", 
                "grievanceclosedate"]
        record = {field:html.unescape(value) for field, value in zip(fields,m)}
        records.append(record)


    while not "Show next row (inactive button)" in r.text:
        payload = get_next_provisional_appointments_payload(icsid, statenum)
        r = s.post(url, data=payload)
        statenum = get_statenum_after_action(r)
        ms = re.findall(prov_appointments_pattern, r.text, flags=re.DOTALL)
        for m in ms:
            fields = ["jobid", "school", "jobtitle", "jobclass", "applicant", 
                    "grievanceclosedate"]
            record = {field:html.unescape(value) for field, value in zip(fields,m)}
            records.append(record)
            
    now = datetime.datetime.today().strftime("%Y-%m-%d %H%M%S")
    df = pd.DataFrame.from_records(records)
    df.to_csv(f"{output_dir}/provisional appointments {now}.csv")
    print(f"{now} Provisional appointments downloaded.")
    
if __name__ == "__main__":
    config_file = "config.toml"
    with open(config_file, "rb") as f:
       config = tomli.load(f)
        
    if not os.path.exists(config['output_dir']):
        os.makedirs(config['output_dir'])
    
    download_jobs(config['output_dir'],config['max_jobs_per_region'],config['found_in_last_run_limit'])
    download_provisional_appointments(config['output_dir'])
