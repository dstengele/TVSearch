#!/usr/bin/env python3

import argparse
import requests

try:
	from lxml import etree
except ImportError:
	try:
		import xml.etree.cElementTree as etree
	except ImportError:
		try:
			import xml.etree.ElementTree as etree
		except ImportError:
			try:
				import cElementTree as etree
			except ImportError:
				try:
					import elementtree.ElementTree as etree
				except ImportError:
					exit(1)
import json

try:
	import settings
except ImportError:
	print("<items><item><title>Konfiguriere mich!</title></item></items>")
	exit()

parser = argparse.ArgumentParser(description='Parse Query from Alfred')
parser.add_argument('query', nargs='*')
args = parser.parse_args()

# Build Request
url = settings.API_ENDPOINT + "secrets/?search=" + "%20".join(args.query)

r = requests.get(url, auth=(settings.USERNAME, settings.PASSWORD))
if r.status_code != 200:
	print("<items><item><title>Passwort falsch?</title></item></items>")
	exit(0)
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
