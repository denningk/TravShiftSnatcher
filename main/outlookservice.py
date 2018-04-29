import requests
import uuid
import json
import time
import re

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
	# Send these headers with all API calls
	headers = { 'User-Agent' : 'python_trav/1.0',
				'Authorization' : 'Bearer {0}'.format(token),
				'Accept' : 'application/json',
				'X-AnchorMailbox' : user_email }

	# Use these headers to instrument calls. Makes it easier
	# to correlate requests and responses in case of problems
	# and is a recommended best practice.
	request_id = str(uuid.uuid4())
	instrumentation = { 'client-request-id' : request_id,
						'return-client-request-id' : 'true' }

	headers.update(instrumentation)

	response = None

	if (method.upper() == 'GET'):
		response = requests.get(url, headers = headers, params = parameters)
	elif (method.upper() == 'DELETE'):
		response = requests.delete(url, headers = headers, params = parameters)
	elif (method.upper() == 'PATCH'):
		headers.update({ 'Content-Type' : 'application/json' })
		response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
	elif (method.upper() == 'POST'):
		headers.update({ 'Content-Type' : 'application/json' })
		response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

	return response

def get_me(access_token):
	get_me_url = graph_endpoint.format('/me')

	# Use OData query parameters to control the results
	#  - Only return the displayName and mail fields
	query_parameters = {'$select': 'displayName,mail'}

	r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

	if (r.status_code == requests.codes.ok):
		return r.json()
	else:
		return "{0}: {1}".format(r.status_code, r.text)

def get_my_messages(access_token, user_email, num = 10):
	get_messages_url = graph_endpoint.format('/me/mailfolders/inbox/messages')

	# Use OData query parameters to control the results
	#  - Only first 10 results returned
	#  - Only return the ReceivedDateTime, Subject, and From fields
	#  - Sort the results by the ReceivedDateTime field in descending order
	query_parameters = {'$top': num,
						'$select': 'ReceivedDateTime,subject,from,toRecipients,id',
						'$orderby': 'receivedDateTime DESC'}

	r = make_api_call('GET', get_messages_url, access_token, user_email, parameters = query_parameters)

	if (r.status_code == requests.codes.ok):
		return r.json()
	else:
		return "{0}: {1}".format(r.status_code, r.text)

def reply_message(access_token, user_email, messageID):
	url_string = '/me/messages/{0}/reply'.format(messageID)
	reply_message_url = graph_endpoint.format(url_string)

	request_body = {
			  		"Comment": "I'll take the trav shift!"
					}

	r = make_api_call('POST', reply_message_url, access_token, user_email, payload = request_body)

	if (r.status_code == requests.codes.ok):
		return r.json()
	else:
		return "{0}: {1}".format(r.status_code, r.text)

def check_shift(access_token, user_email, shift_wanted, date_wanted=""):
	searching_for_shift = True

	while searching_for_shift:
		currMessage = get_my_messages(access_token, user_email, num = 1)
		if len(currMessage['value'][0]['toRecipients']) > 0 :
			#print(currMessage['value'])
			recipientEmail = currMessage['value'][0]['toRecipients'][0]['emailAddress']['address']
		
			fromEmail = currMessage['value'][0]['from']['emailAddress']['address']
			#print(recipientEmail.lower())
			if recipientEmail.lower() == 'travellerstaff@mail.wlu.edu':
			#if recipientEmail.lower() == 'denningk18@mail.wlu.edu':
				#print("yes")
				currSub = currMessage['value'][0]['subject']
				shift_offered = [i for i in shift_wanted if i in currSub.lower()]
				
				#print(shift_offered)
				if (len(shift_offered) > 0) and ("tonight" in currSub.lower()) and re.search('4/3$',currSub): #re.search('3/2$', currSub) == None and re.search('3/3$', currSub) == None and ("3/9" not in currSub) and ("3/10" not in currSub) and ("3/24" not in currSub):
					
					
					
					messID = currMessage['value'][0]['id']
					reply_message(access_token,user_email,messID)

					person = currMessage['value'][0]['from']['emailAddress']['name']
					searching_for_shift = False

					print("Success!")

					return person, shift_offered[0]
		time.sleep(1)