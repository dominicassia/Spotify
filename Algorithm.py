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

def executionTime(tStart):

    ''' executionTime() calculates the execution time between tStart and when this function is called
    
        ( float ) --> ' Executed in float seconds ' 

        ( tStart ) --> ' Executed in float seconds ' 

        This function uses the time module to clock tEnd when the function is called & calculate the difference in time 
        between tStart and tEnd

    '''

    tEnd = time.time()                                                      # End Clock
    exTime = round(tEnd-tStart, 4)                                          # Calculate execution & round execution time
    print('\tExecuted in', exTime, 's.\n') 

def initialize():

    ''' initialize() prepares essential data for the rest of the algorithm.

        (  ) --> dict

        (  ) --> tokenData

        * dict = { str, str, str, str, str, str, str}

        dict returns the values: token, clientID, clientSecret, userID, refreshToken, redirectURI, path        

        Crucial auth data is retrieved from tokenData.json & is verified to still be valid ( GET & save new auth if not )

    '''

    def clientInfo():

        ''' Retrieve data from tokenData.json and return as dictionary 
        
        (  ) --> dict

        * dict = { str, str, str, str, str, str, str}

        dict returns the values: token, clientID, clientSecret, userID, refreshToken, redirectURI, path
        
        '''

        print('> Extracting Data.')

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

            token = refresh(tokenData['refreshToken'], tokenData['clientID'], tokenData['clientSecret'])

            # save the new auth token to tokenData.json

            with open(tokenData['path'], 'r+') as r:

                data = json.load(r)
                data['data'][0]['token'] = token

                with open(tokenData['path'], 'w') as w:

                    json.dump(data, w, indent=4)

                print('\tSaved.\n')

                # use the new token to request the user's profile data

                print('> Retrieving user data.')

                temp = userInfo(token, tokenData['userID'])

                print('\tStatus: ', temp.status_code)

        # Otherwise the auth token is still valid, assign & return display name & token

        else:

            print('\tValid token.\n')

            token = tokenData['token']

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

    def refresh(refreshToken, clientID, clientSecret):
        
        ''' refresh() utilizes the refresh token in order to obtain a new auth token via POST request
        
            ( str, str, str ) --> str

            ( refresh token, client ID, client secret ) --> auth token

        '''

        data = { 'grant_type': 'refresh_token', 'refresh_token': refreshToken }

        response = requests.post('https://accounts.spotify.com/api/token', data=data, auth=(clientID, clientSecret), timeout=10)
        
        # This POST returns JSON with the new access token
        
        r = response.json()

        print('\tNew token obtained.')
        return r['access_token']

    # Call functions inside initialize()

    print('\n')

    tStart = time.time()
    tokenData = clientInfo()
    executionTime(tStart)

    tStart = time.time()
    token, displayName = validate(tokenData)
    executionTime(tStart)

    tStart = time.time()
    tokenData = clientInfo()
    executionTime(tStart)
    
    return tokenData

def playback(token, tempF):

    ''' playback() monitors the user's playback and determines what is eligible to be added to listeningData.json to be further analyzed 
    
        ( str, str ) --> function will loop or call other code to come back to the same loop

        ( token, tempF )
    '''

    def GETplayback(token):

        ''' Utilize a GET request to determine the playback state of the user's application & information
            pertaining to what is playing
        
            ( str ) --> dict

            ( auth token ) --> responseValues

            * dict contains: { str, str, str, str, str, str, bool }

            * responseValues: trackName, trackURI, trackProgress, trackDuration, artistName, artistURI, playing

            Timeout:            Sleep for 5s    --> main()
            Connection Error:   Sleep 20s       --> main()

            <401> response:     Invalid token   --> main()
            <204> response:     No data         --> Sleep 20s

         '''

        # https://developer.spotify.com/documentation/web-api/reference/player/get-information-about-the-users-current-playback/

        url = 'https://api.spotify.com/v1/me/player'
        headers = {'Authorization': 'Bearer ' + token }

        try:
            # This GET request returns response containing a user's current listening status

            response = requests.get(url=url, headers=headers, timeout=10)
            
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

        print('Status: ', response.status_code, '\n')

        # Unauthorized

        if response.status_code == 401:

            print('\tUnauthorized')
            print('\t----- restart -----')

            main()

        # No data

        if response.status_code == 204:

            print('\tNo data')
            print('\tSleep: 20 s\n')

            time.sleep(20)

            print('\t----- restart -----\n')

            playback(token, tempF)

        r = json.loads(str(response.text))    

        # Create dictionary to return

        responseValues = {
            'trackName'         : r['item']['name'], 
            'trackURI'          : r['item']['uri'],
            'trackProgress'     : r['progress_ms'],
            'trackDuration'     : r['item']['duration_ms'],
            'artistName'        : r['item']['artists'][0]['name'],
            'artistURI'         : r['item']['artists'][0]['uri'],
            'playing'           : r['is_playing']
        }

        return responseValues

def main():

    ''' 
        Optimized, oraganized, and consice extension of SpotifyAlgorithm.py

        Function map:

        initialize()        returns dict tokenData containing the contents of tokenData.json    
            clientInfo()    grabs token info from tokenData.json
            validate()      verifies the auth token is valid
            userInfo()      uses GET to request the user's profile data
            refresh()       grabs new auth token & saves to tokenData.json

        playback()
            GETplayback()
            moreThanHalf()
            tempReturn()
            duration()

    '''

    # Call functions inside main()

    tokenData = initialize()

    playback( tokenData['token'], tempF='' )

# Call main

main()