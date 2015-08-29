import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import logging
import json

import utils
import submit

## =====================================================================
## LOGGING CONFIGURATION
## =====================================================================

## =====================================================================
## DRIVER
## =====================================================================
class Driver(object):
	
	def __init__(self):
		pass

	def drive(self, deployer):
		# get main page
		main_page = deployer.get_main_page()
		
		# recursively crawl all pages and extract the forms
		out = utils.run_command('cd {} && {}'.format(
			os.path.join(os.path.dirname(__file__), 'extract'),
			'scrapy crawl form -o forms.json -a start_url="{}"').format(main_page))

		with open(os.path.join(os.path.dirname(__file__), 'extract', 'forms.json')) as json_forms:
			try:
				forms = json.load(json_forms)
			except:
				forms = []

		# generate input for the forms and submit them
		for form in forms:
			submit.submit(form)

		out = utils.run_command('cd {} && {}'.format(
			os.path.join(os.path.dirname(__file__), 'extract'), 
			'rm -f forms.json'))
		