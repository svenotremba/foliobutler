import json
#from flask import json
import requests

base_url = 'https://www.foliobutler.com/api/'
auth_url = base_url + "auth/"
folio_url = base_url + "v1/folio/"

def get_token(user, key):
	resp, data = post_json(auth_url, {'identity': user, 'password': key})
	return data["data"]['access_token']

def get_json(url, token=None, payload=None):
	headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
	resp = requests.get(url, headers=headers, params=payload)
	return resp, json.loads(resp.text)

def post_json(url, data=None, token=None):
	data = json.dumps(data)
	headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
	resp = requests.post(url, headers=headers, data=data)
	return resp, json.loads(resp.text)

def get_folios(token):
	resp, data = get_json(folio_url , token)
	if resp.status_code == 200:
		return data['data']
	raise Exception(resp.text)

def get_folio(token, id):
	resp, data = get_json(folio_url + "{}/".format(id) , token)
	if resp.status_code == 200:
		return data['data']
	raise Exception(resp.text)
