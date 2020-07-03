# Optimized, oraganized, and consice extension of SpotifyAlgorithm.py

# Function map:

#   initialize()
#       clientInfo()    grabs token info from tokenData.json
#       validate()      verifies the auth token is valid
#       userInfo()      uses GET to request the user's profile data
#       refresh()       grabs new auth token & saves to tokenData.json

#   loop()
#       

#####################################################

# Libraries

import base64               # Encode
import urllib.parse         # Encode
import requests             # cURL 
import json                 # Parse
import time                 # Execution time
import datetime             # Sorting timestamps
import operator             # Sorting specific indices
import functools            # Caching
import tempfile             # Temporary files

#####################################################

def initialize():

    def clientInfo():

        ''' Retrieve data from tokenData.json and return as dictionary '''

        path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\tokenData.json'

        with open(path, 'r') as t:                                          # Open tokenData.json
            temp = json.load(t)                                             # Load as object

            tokenData = {

                'token'         :   temp['data'][0]['token'],
                'clientID'      :   temp['data'][0]['clientID'],
                'clientSecret'  :   temp['data'][0]['clientSecret'],
                'userID'        :   temp['data'][0]['clientUserID'],
                'refreshToken'  :   temp['data'][0]['refreshToken'],
                'redirectURI'   :   temp['data'][0]['redirectURI']

            }

            return tokenData

    def validate(tokenData):

        ''' Uses GET request to grab the user's profile data to verify if the auth token is valid '''

        # userInfo() returns the response of requesting the user's profile data

        temp = userInfo(tokenData['token'], tokenData['userID'])

        print('\tStatus: ', temp.status_code)

        # Check if token is valid, If response if <401> get a new token

        if temp.status_code == 401:

            print('\tObtaining new token.')                                                           
            token = refresh(refreshToken, clientID, clientSecret)

            # Write the token to tokenData.JSON

            with open(path, 'r+') as r:

                # Load, Assign
                data = json.load(r)
                data['data'][0]['token'] = token

                with open(path, 'w') as w:

                    # Dump
                    json.dump(data, w, indent=4)

                print('\tSaved.\n')

                print('> Retrieving user data.')
                temp = userInfo(token, userID)
                print('\tStatus: ', temp.status_code)
        else:
            print('\tValid token.\n')
            print('> Retrieving user data.')
            print('\tStatus: ', temp.status_code)


        name = temp.json()
        displayName = name['display_name']
        print('\tUser:', displayName, '\n')

        return token, displayName

    def userInfo(token, userID):

        # Check status of saved token

        url = 'https://api.spotify.com/v1/users/' + userID
        headers = {'Authorization':'Bearer ' + token }

        try:
            response = requests.get(url=url, headers=headers, timeout=10)

        # https://requests.readthedocs.io/en/master/user/quickstart/#errors-and-exceptions

        except requests.ConnectionError:

            print('\n\tConnection Error')

            print('\tSleep: 20 sec\n')
            time.sleep(20)

            print('\t----- restart -----\n')
            main()

        except requests.TimeoutError:

            print('\tTimeout')

            print('\tSleep: 5 sec')
            time.sleep(5)

            print('\t----- restart -----\n')
            main() 

        return response

    # Call functions inside initialize()

    tokenData = clientInfo()
    token, displayName = validate(tokenData)
 
def main():

    # Call functions inside main()

    initialize()