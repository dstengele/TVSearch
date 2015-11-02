#!/usr/bin/env python3

import argparse
import requests
from lxml import etree
import json

import settings

parser = argparse.ArgumentParser(description='Parse Query from Alfred')
parser.add_argument('query', nargs='*')
args = parser.parse_args()

# Build Request
url = settings.API_ENDPOINT + "secrets/?search=" + " ".join(args.query)

r = requests.get(url, auth=(settings.USERNAME, settings.PASSWORD))
searchResults = json.loads(r.content.decode())

# Generate Output XML
root = etree.Element('items')

for result in searchResults['results']:
	resultToAdd = etree.SubElement(root, 'item', uid='', arg='')
	title = etree.SubElement(resultToAdd, 'title')
	subtitle = etree.SubElement(resultToAdd, 'subtitle')
	textToCopy = etree.SubElement(resultToAdd, 'text', type='copy')
	textToLargetype = etree.SubElement(resultToAdd, 'text', type='largetype')


	# Get secret data (current_revision)
	# https://github.com/trehn/teamvault/wiki/API-documentation#get-the-secret-data
	url = result['current_revision']
	teamvaultId = result['api_url'].split('/')[-2]
	r = requests.get(url, auth=(settings.USERNAME, settings.PASSWORD))
	currentRevision = json.loads(r.content.decode())

	# We need to go deeper! (data_url)
	url = currentRevision['data_url']
	r = requests.get(url, auth=(settings.USERNAME, settings.PASSWORD))
	currentRevisionData = json.loads(r.content.decode())
	password = currentRevisionData['password']

	resultToAdd.set('uid', teamvaultId)
	resultToAdd.set('arg', password)
	title.text = result['name']
	subtitle.text = result['username']
	textToCopy.text = password
	textToLargetype.text = password

# Output XML
s = etree.tostring(root, pretty_print=True)
print(s.decode())
