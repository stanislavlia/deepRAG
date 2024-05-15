import requests
import json
import os
import pandas as pd
import logging
import sys

BACKEND_HOST = "http://retrieval_app:8012/"
TMP_DIR = "/app/tmp"


def search_in_collection(query, n_results=4):

	url = os.path.join(BACKEND_HOST, "query/")
	print(url)
	headers = {'Content-Type': 'application/json'}

	request_json = json.dumps({"query" : query,
				    			"n_results" : n_results})	
	search_result_response = requests.post(url=url, data=request_json, headers=headers)

	return search_result_response


def send_pdf_to_server(binary_data, pdf_name):
    url = f"{BACKEND_HOST}upload_pdf"
    
    # Save file to temporary file
    tmp_path = os.path.join(TMP_DIR, pdf_name)
    with open(tmp_path, "wb") as f:
        f.write(binary_data)
    
    # Open the file in binary mode and send as 'application/pdf'
    with open(tmp_path, "rb") as f:
        files = {'file': (pdf_name, f, 'application/pdf')}
        logging.info(f"Sending file {pdf_name} to backend")
        response = requests.post(url, files=files)
    
    logging.info(f"Status code of sending {pdf_name}: {response.status_code}")
    return response

def parse_search_result(search_result_response):

	search_result_response = search_result_response.json()
      
	documents = search_result_response["docs"]
	metadatas = search_result_response["metadatas"]
      
	if search_result_response["chunks_retrieved"] > 0:

		pages_data = [{
					"document" : documents[i],
						"page" : metadatas[i]["page"],
						"source" : metadatas[i]["source"]
						}  for i in range(len(documents))]

		return pages_data #list of dicts
    
	return []
