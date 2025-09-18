#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from datetime import date
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import fromstring
import os
import random
from sqlalchemy import create_engine

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

@click.command()
@click.option('--country', default='Canada')
def ds(country):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	res = []

	sp_tree = ET.parse(os.path.join(os.getcwd(), 'SearchSightseeingPriceRequest.xml'))
	si_tree = ET.parse(os.path.join(os.getcwd(), 'SearchItemInformationRequest.xml'))

	engine = create_engine('sqlite:///destServ.db')
	services_raw = engine.execute("SELECT * FROM destination_service_raw WHERE country='{0}';".format(country))

	last_city_code = None
	last_item_code = None
	entry = None

	for row in services_raw:
		pprint.pprint(row)

		sp_tree.find('.//ItemDestination').set('DestinationCode', row['city_code'])
		sp_tree.find('.//ItemCode').text = row['item_code']

		from_d = datetime.datetime.strptime(row['dates_from'], '%d-%b-%y').date()
		to_d = datetime.datetime.strptime(row['dates_to'], '%d-%b-%y').date()

		n_d = datetime.datetime.now().date()

		# pprint.pprint(to_d)
		# pprint.pprint(n_d)

		# pprint.pprint(to_d < n_d)

		if to_d < n_d:
			pprint.pprint('To date is less than now date... skipping...')
			continue

		search_d = to_d - datetime.timedelta(days=1)
		sp_tree.find('.//TourDate').text = search_d.strftime('%Y-%m-%d')

		min_pax = row['min_pax']
		sp_tree.find('.//NumberOfAdults').text = min_pax

		if row['pax_type'] == 'Child':
			child_from_age = int(row['age_from'])
			for i in range(int(row['min_pax'])):
				# GTA API doesn't accept child under age 2...
				sp_tree.find('.//Children').append(fromstring('<Age>{0}</Age>'.format(child_from_age + 1 if child_from_age >= 2 else 10)))
		# pprint.pprint(row['country'])
		# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

		try:
			rp = requests.post(url, data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
		except OSError:
			pprint.pprint('Error: ignoring OSError...')
			continue

		if row['pax_type'] == 'Child':
			parent = sp_tree.find('.//Children')
			for child in list(parent):
				parent.remove(child)

		rp_tree = ET.fromstring(rp.text)

		# pprint.pprint(rp.text)	

		if not len(list(rp_tree.find('.//SightseeingDetails'))):
			pprint.pprint('No sightseeing price returned...')
			continue
		
		rp = {}

		# entry
		if last_city_code == row['city_code'] and last_item_code == row['item_code']:
			mumble = 1
		else:
			entry = {}
			entry['city_code'] = row['city_code']
			entry['item_code'] = row['item_code']
			entry['name'] = rp_tree.find('.//Item').text
			if rp_tree.find('.//Duration') != None:
				entry['duration'] = rp_tree.find('.//Duration').text
			if rp_tree.find('.//PleaseNote') != None:				
				entry['please_note'] = rp_tree.find('.//PleaseNote').text
			entry['currency'] = rp_tree.find('.//ItemPrice').get('Currency')
			entry['child_age_from'] = row['age_from']
			entry['child_age_to'] = row['age_to']

			entry['policy'] = ''
			for charge_condition in rp_tree.find('.//ChargeConditions'):
				if charge_condition.get('Type') == 'cancellation':
					for conditoin in charge_condition:
						if conditoin.get('Charge') == 'true':
							entry['policy'] += 'Charge(FromDay: ' + str(conditoin.get('FromDay')) + ' ToDay: ' + str(conditoin.get('ToDay')) + ') '
						else:
							entry['policy'] += 'Free(FromDay: ' + str(conditoin.get('FromDay')) + ') '

			entry['rate_plan'] = []
			res.append(entry)
		
		tour_ops = rp_tree.find('.//TourOperations')

		if row['pax_type'] == 'Child':
			if len(list(tour_ops)) == 1:
				for rate_plan in entry['rate_plan']:
					if rate_plan['min_pax'] == row['min_pax'] and rate_plan['pax_type'] == 'Adult':
						rp['price'] = float(rp_tree.find('.//ItemPrice').text) - float(rate_plan['price'])
						break
			else:
				for rate_plan in entry['rate_plan']:
					if rate_plan['min_pax'] == row['min_pax'] and rate_plan['pax_type'] == 'Adult':
						rp['prices'] = []			
						
						for tour_op in tour_ops:
							child_tour_name = ''
							if tour_op.find('.//SpecialItem') != None:
								child_tour_name = tour_op.find('.//SpecialItem').text
							else:
								child_tour_name = tour_op.find('.//TourLanguage').text

							child_tour_price = tour_op.find('.//ItemPrice').text
							for adult_tour_op in rate_plan['prices']:
								if child_tour_name == adult_tour_op['name']:
									op_entry = {}
									op_entry['name'] = child_tour_name
									op_entry['price'] = float(child_tour_price) - float(adult_tour_op['price'])
									rp['prices'].append(op_entry)

						break

		else:
			# rp['price'] = rp_tree.find('.//ItemPrice').text
			if len(list(tour_ops)) == 1:
				rp['price'] = rp_tree.find('.//ItemPrice').text
			else:
				rp['prices'] = []			
				for tour_op in tour_ops:
					op_entry = {}
					if tour_op.find('.//SpecialItem') != None:
						op_entry['name'] = tour_op.find('.//SpecialItem').text
					else:
						op_entry['name'] = tour_op.find('.//TourLanguage').text
					op_entry['price'] = tour_op.find('.//ItemPrice').text
					rp['prices'].append(op_entry)


		rp['min_pax'] = row['min_pax']
		rp['pax_type'] = row['pax_type']
		rp['from_date'] = from_d.strftime('%Y-%m-%d')
		rp['to_date'] = to_d.strftime('%Y-%m-%d')
		entry['rate_plan'].append(rp)

		last_city_code = row['city_code']
		last_item_code = row['item_code']

		pprint.pprint(entry)
		

if __name__ == '__main__':
	ds()