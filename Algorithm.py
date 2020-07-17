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

            * dict contains: { str, str, str, str, str, str, bool, str }

            * responseValues: trackName, trackURI, trackProgress, trackDuration, artistName, artistURI, playing, timestamp

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
            'playing'           : r['is_playing'],
            'timestamp'         : r['timestamp']
        }

        return responseValues

    def moreThanHalf(duration, progress):

        ''' moreThanHalf() is a simple logic function to determine if the songs progess is more than half of the songs duration

            ( str, str ) --> bool

            ( duration, progress ) --> bool
        
        '''

        if progress > (int(duration / 2)):

            return True
            
        else:

            return False

    def tempReturn(tempF):

        ''' tempReturn() works with the temp file created in order to return the contents of the temp file as a string

            ( str ) --> str     
            
            **Initially this is the case.. Once a temp file is created:    
            
            ( temp file obj ) --> str
        
            < Utilizes the tempfile library >
        '''

        try:

            tempF.seek(0)
            return str(tempF.read())

        except ValueError:

            tempF = tempfile.TemporaryFile(mode='w+', dir=None)
            tempF.write( str(response['trackURI']) )

            tempF.seek(0)
            return str(tempF.read())

    def duration(response, tempF):

        ''' duration() monitors the progress of a song's playback by using response data from GETplayback(), 
            temporarily storing the CURL response while waiting for more than half the song to be listened to 
            before writing data to listeningData.json
        
            ( dict, '' or temp file obj ) --> varying function calls 

            ( resonse, tempF ) --> playback() or write to listeningData.json

            Utilizes tempfile, requests, time libraries

            https://www.tutorialspoint.com/generate-temporary-files-and-directories-using-python
        '''

        try:
            if tempF == '':

                tempF = tempfile.TemporaryFile(mode='w+', dir=None)
                tempF.write( str(response['trackURI']) )

        except AttributeError or ValueError:

            tempF = tempfile.TemporaryFile(mode='w+', dir=None)
            tempF.write( str(response['trackURI']) )        

        if response['playing'] == True:

            print('Playback:', response['trackName'], '|', response['artistName'], '\n')

            if moreThanHalf( response['trackDuration'], response['trackProgress'] ) == True and response['trackURI'] == tempReturn(tempF):

                # More than half of the same song has been listened to, add to listening history

                if response['trackProgress'] <= ( (response['trackDuration'] / 4) *3):

                    print('\tPlayback progress:', round((response['trackProgress'] / response['trackDuration'])*100, 1), '%')
                    print('\n\tAdding to listening history\n')
                
                    # Add to listening history here:

                    localData(token, response)

                    print('\tDone.\n')

                    print('\tSleep:', round( ( response['trackDuration'] - response['trackProgress'] ) / 2000, 1), 's\n')
                    time.sleep( ( response['trackDuration'] - response['trackProgress'] ) / 2000)

                    tempF.close()

                else:

                    print('\tPlayback progress:', round((response['trackProgress'] / response['trackDuration'])*100, 1), '%')

                    print('\tSleep:', round( ( response['trackDuration'] - response['trackProgress'] ) / 2000, 1), 's\n')
                    time.sleep( ( response['trackDuration'] - response['trackProgress'] ) / 2000)

                    tempF.close()

                print('\t----- restart -----\n')
                playback(token, tempF)

            elif response['trackURI'] != tempReturn(tempF):

                # The User skipped the song before getting halfway, restart the function
                print('\tSkipped\n')
                tempF.close()

                print('\t----- restart -----\n')
                playback(token, tempF)

            elif moreThanHalf( response['trackDuration'], response['trackProgress'] ) == False:

                # Calculate and wait for the remainder of half the song

                if response['trackProgress'] < ( response['trackDuration'] / 4 ):

                    print('\tPlayback progress:', round( ( response['trackProgress'] / response['trackDuration'] ) *100, 1), '%')
                    print('\tSleep:', round( ( ( response['trackDuration'] / 2 ) - response['trackProgress']) / 2000, 1), 's\n')
                    time.sleep( ( ( response['trackDuration'] / 2 ) - response['trackProgress']) / 2000 )

                elif response['trackProgress'] > ( response['trackDuration'] / 4 ):

                    print('\tPlayback progress:', round((response['trackProgress'] / response['trackDuration'])*100, 1), '%')
                    print('\tSleep:', round( ( ( response['trackDuration'] / 2 ) - response['trackProgress']) / 1000, 1), 's\n')
                    time.sleep( int( int( response['trackDuration'] / 2 ) - response['trackProgress']) / 1000)

                print('\t----- restart -----\n')
                playback(token, tempF)

        elif response['playing'] == False:

            # The music is not playing

            print('\tNo current playback')
            print('\tSleep: 10 s\n')

            time.sleep(10)

            print('\t----- restart -----\n')
            playback(token, tempF)

        else:

            print('\tFallback case.\n')

    # Call functions within playback()

    response = GETplayback(token)
    duration(response, tempF)

def localData(token, response):
    
    ''' localData() writes history to listeningData.json and update genreData.json

        ( dict ) --> save data to .json

        * dict contains: { str, str, str, str, str, str, bool, str }

        * response: trackName, trackURI, trackProgress, trackDuration, artistName, artistURI, playing, timestamp

        Functions:
            convertTimestamp()
            writeHistory()
            sortHistory()
            checkGenre()
            writeGenre()
                writeArtist()
                writeSong()

            popularity()
    ''' 

    def convertTimestamp(response):

        ''' convertTimestamp() converts the timestamp stored with the current playback's data
        
            ( dict ) --> dict

            UNIX ms --> YYYY-MM-DD HH:MM:SS.MS

            # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
            # https://stackoverflow.com/questions/36103448/convert-from-unix-timestamp-with-milliseconds-to-hhmmss-in-python
        '''

        response['timestamp'] = datetime.datetime.fromtimestamp( response['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')

        return response

    def writeHistory(response):

        ''' Write dict data to listeningData.json (target)

            ( dict ) --> write to target

            ( response ) --> write to target

            listeningData.json entry format:

            [{
                timestamp   : " str (YYYY-MM-DD HH:MM:SS.MS)"
                name        : " str "
                uri         : " str (spotify:track:________________________)"
            }]

            * dict contains: { str, str, str, str, str, str, bool, str }

            * response: trackName, trackURI, trackProgress, trackDuration, artistName, artistURI, playing, timestamp
        '''

        path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\listeningData.json'

        with open(path) as fileRead:

            # Load file as json object, append format, & dump to json file

            listeningData = json.load(fileRead)

            lst = [{
                'timestamp' :   response['timestamp'],
                'name'      :   response['trackName'],
                'URI'       :   response['trackURI']
            }]

            listeningData['items'][0]['data'].append(lst)

            # Write/dump to json file

            with open(path, 'r+') as fileWrite:

                json.dump(listeningData, fileWrite, indent=4) 

            return path

    def sortHistory(path):

        ''' sortHistory() ensures that all timestamps within listeningData.json are in chronlogical order
        
            ( str ) --> chronologically sorted json file **

            ** json format must be as specified in jsonStructures.txt
        '''

        with open(path) as fileRead:

            # Load file as json object, append all data to local list, sort, & dump to json file

            listeningData = json.load(fileRead)

            lst = []

            for i in range( len(listeningData['items'][0]['data'])):

                # lst format: [[ timestamp, name, uri ], ... ]

                lst.append([

                    listeningData['items'][0]['data'][i][0]['timestamp'],
                    listeningData['items'][0]['data'][i][0]['name'],
                    listeningData['items'][0]['data'][i][0]['URI'],

                ])

            # Sort outter list by inner list using itemgetter
                # https://stackoverflow.com/questions/4174941/how-to-sort-a-list-of-lists-by-a-specific-index-of-the-inner-list

            lst = sorted( lst, key=operator.itemgetter(0) )

            # Put list into json format and write back to file

            for j in range(len(lst)):

                lst[j] = [{

                    'timestamp' :   str( lst[j][0] ),
                    'name'      :   lst[j][1],
                    'URI'       :   lst[j][2]

                }]

            # Write to file

            with open(path, 'r+') as fileWrite:

                json.dump(listeningData, fileWrite, indent=4) 

    def checkLocalData(response):
        
        ''' checkLocalData() takes artist and track data and checks the contents of genreData.json and determine whether artist and 
            track data must be added or updated

            verifyArtist()
            verifyTrack() 

            writeArtist()
            writeTrack()


        '''


    def verifyArtist(path, artistURI):

        ''' verifyArtist() checks the contents of the json file path for the artist's URI
            The function returns the index of the artist if found and False bool if not

            ( str, str ) --> int **or bool

            ( path, artistURI ) --> int **or False

        '''

        with open(path) as fileRead:

            genreData = json.load(fileRead)

            for i in range(len(genreData['items'][0]['data'])):

                if genreData['items'][0]['data'][i]['artist'][0]['URI'] == artistURI:

                    # return the index of the artist

                    return i 

    def verifyTrack(path, trackURI, artistIndex):

        ''' verifyTrack() checks the contents of the json file path for the track's URI
            The function returns the index (int) of the track if found and False (bool) if not

            * To search through every song in the file (artist index not known) set artistIndex = False (bool)

            Artist index is known:
                ( str, str, int ) --> index of track (int) or False if track not found (bool)

            Artist index is not known:
                ( str, str, bool ) --> index of track (int) or False if track not found (bool)

        '''

        # Search the entire file

        if type(artistIndex) == bool and artistIndex == False:

            # The artist index is not known, search through all songs in the file
            
            with open(path) as fileRead:

                genreData = json.load(fileRead)

                # For every artist in the file

                for h in range(len(genreData['items'][0]['data'])):

                    # For every song within that artist

                    for i in range(len(genreData['items'][0]['data'][h]['artist'][0]['songs'])):

                        if genreData['items'][0]['data'][h]['artist'][0]['songs'][i]['song'][0]['URI'] == trackURI:

                            # Found the track, return the index of the track

                            x = 0
                            return i 
                            break

                        else:
                            x += 1

                if x != 0:

                    # The track was not found, return false

                    return False

        # Given an artist index

        elif type(artistIndex) == int:

            # The artist's index is known, search for the song there

            with open(path) as fileRead:

                genreData = json.load(fileRead)

                for i in range(len(genreData['items'][0]['data'][artistIndex]['artist'][0]['songs'])):

                    if genreData['items'][0]['data'][h]['artist'][0]['songs'][i]['song'][0]['URI'] == trackURI:

                        # Found the track, return the index of the track

                        x = 0
                        return i 
                        break

                    else:
                        x += 1
                
                if x != 0:

                    # The artist was not found

                    return False

    # Call functions within localData()

    print('\t> Converting timestamp\n')
    response = convertTimestamp(response)

    print('\t> Writing listening history\n')
    path = writeHistory(response)

    print('\t> Sorting listeningData.json\n')
    sortHistory(path)

    print('\t> Checking genreData.json')
    checkLocalData(response)

    # TODO: Check if the song / artist is already in genreDara.json

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
            duration()      * Calls localData()

        localData()
            convertTimestamp()
            writeHistory()
            sortHistory()
            checkGenre()
            writeGenre()
                writeArtist()
                writeSong()

            popularity()


    '''

    # Call functions inside main()

    tokenData = initialize()

    playback( tokenData['token'], tempF='' )

# Call main

main()

# TODO: Think about determining the different genres and checking if the artist and song data is added to genreData.json after something is added to listeningData.json as mentioned