import requests
import json
import os
import pandas as pd
import logging
import sys

BACKEND_HOST = "http://retrieval_app:8012/"
TMP_DIR = "/app/tmp"

def search_in_collection(query, n_results=4, collection_name="test"):

	url = os.path.join(BACKEND_HOST, f"collections/query/{collection_name}")
	print(url)
	headers = {'Content-Type': 'application/json'}

	request_json = json.dumps({"query" : query,
				    			"n_results" : n_results})

	
	search_result_response = requests.post(url=url, data=request_json, headers=headers)

	return search_result_response


def send_pdf_to_server(binary_data, pdf_name, collection_name="test"):
    url = f"{BACKEND_HOST}collections/upload_doc/{collection_name}"
    
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
	ids = search_result_response["ids"][0]
	distances = search_result_response["distances"][0]
	documents = search_result_response["documents"][0]
	metadatas = search_result_response["metadatas"][0]

	pages_data = [{"id" : ids[i], 
				   "distance" : distances[i],
				   "document" : documents[i],
					"page" : metadatas[i]["page"],
					"source" : metadatas[i]["source"]
					}  for i in range(len(ids))]

	return pages_data #list of dicts
