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

    ''' initialize() prepares essential data for the rest of the algorithm.

        Crucial auth data is retrieved from tokenData.json & is verified to still be valid ( GET & save new auth if not )

    '''

    def clientInfo():

        ''' Retrieve data from tokenData.json and return as dictionary 
        
        (  ) --> dict

        * dict = { str, str, str, str, str, str, str}

        dict returns the values: token, clientID, clientSecret, userID, refreshToken, redirectURI, path
        
        '''

        path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\tokenData.json'

        with open(path, 'r') as t:                                          # Open tokenData.json
            temp = json.load(t)                                             # Load as object

            tokenData = {

                'token'         :   temp['data'][0]['token'],
                'clientID'      :   temp['data'][0]['clientID'],
                'clientSecret'  :   temp['data'][0]['clientSecret'],
                'userID'        :   temp['data'][0]['clientUserID'],
                'refreshToken'  :   temp['data'][0]['refreshToken'],
                'redirectURI'   :   temp['data'][0]['redirectURI'],
                'path'          :   path

            }

            return tokenData

    def validate(tokenData):

        ''' Uses GET request to grab the user's profile data to verify if the auth token is valid via status of the response 
        
            ( dict ) --> str, str

                validate( dict ) --> auth token & the user's display name
    
                * dict must contain: token, clientID, clientSecret, userID, refreshToken, redirectURI, path

            If the GET request status is <401> the auth token is not valid & refresh() will be called & 
            the new auth token will be saved to tokenData.json

        '''

        # userInfo() returns the request's response

        temp = userInfo(tokenData['token'], tokenData['userID'])

        print('\tStatus: ', temp.status_code)

        # If the request's response is <401> the auth token is not vaid & must be refreshed

        if temp.status_code == 401:

            print('\tObtaining new token.')     

            # refresh() returns a new auth token

            token = refresh(refreshToken, clientID, clientSecret)

            # save the new auth token to tokenData.json

            with open(tokenData['path'], 'r+') as r:

                data = json.load(r)
                data['data'][0]['token'] = token

                with open(tokenData['path'], 'w') as w:

                    json.dump(data, w, indent=4)

                print('\tSaved.\n')

                # use the new token to request the user's profile data

                print('> Retrieving user data.')

                temp = userInfo(token, userID)

                print('\tStatus: ', temp.status_code)

        # Otherwise the auth token is still valid, assign & return display name & token

        else:

            print('\tValid token.\n')
            print('> Retrieving user data.')
            print('\tStatus: ', temp.status_code)

        # Assign display name

        name = temp.json()
        displayName = str(name['display_name'])
        print('\tUser:', displayName, '\n')

        return token, displayName

    def userInfo(token, userID):

        ''' userInfo() requests the user's profile data & returns the response 
        
        ( str, str ) --> response

        ( token, userID ) --> response
 
        '''

        # Request the user's profile data

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