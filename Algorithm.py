# Dependencies
import base64               # Encode
import urllib.parse         # Encode
import requests             # cURL 
import json                 # Parse
import time                 # Execution time
import datetime             # Sorting timestamps
import operator             # Sorting specific indices
import functools            # Caching
import tempfile             # Temporary files

import playlist             # playlist functions
import spotify_requests     # spotify requests
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

def playback(token, tempF, multiplier):

    ''' playback() monitors the user's playback and determines what is eligible to be added to listeningData.json to be further analyzed 
    
        ( str, str ) --> function will loop or call other code to come back to the same loop

        ( token, tempF )
    '''

    def GETplayback(token, multiplier):

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

            multiplier += 1 

            print('\tNo data')

            # Check multiplier value

            if multiplier % 3 == 0 :

                # The 204 status has been recieved for 60 sec ( 20sec * 3times ) 

                print('\n> Analyzing playlists\n')

                playlists(token)

            print('\tSleep: 20 s\n')

            time.sleep(20)

            print('\t----- restart -----\n')

            playback(token, tempF, multiplier)

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

    def duration(response, tempF, multiplier):

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

            multiplier = 0.0

            print('Playback:', response['trackName'], '|', response['artistName'], '\n')

            if moreThanHalf( response['trackDuration'], response['trackProgress'] ) == True and response['trackURI'] == tempReturn(tempF):

                # More than half of the same song has been listened to, add to listening history

                if response['trackProgress'] <= ( (response['trackDuration'] / 4) *3):

                    print('\tPlayback progress:', round((response['trackProgress'] / response['trackDuration'])*100, 1), '%')
                    print('\n\t      Adding to listening history\n')
                
                    # Add to json here:

                    localData(token, response)

                    multiplier = 0.0

                    print('\t      Done.\n')

                    print('\tSleep:', round( ( response['trackDuration'] - response['trackProgress'] ) / 2000, 1), 's\n')
                    time.sleep( ( response['trackDuration'] - response['trackProgress'] ) / 2000)

                    tempF.close()

                else:

                    print('\tPlayback progress:', round((response['trackProgress'] / response['trackDuration'])*100, 1), '%')

                    print('\tSleep:', round( ( response['trackDuration'] - response['trackProgress'] ) / 2000, 1), 's\n')
                    time.sleep( ( response['trackDuration'] - response['trackProgress'] ) / 2000)

                    tempF.close()

                print('\t----- restart -----\n')
                playback(token, tempF, multiplier)

            elif response['trackURI'] != tempReturn(tempF):

                # The User skipped the song before getting halfway, restart the function
                print('\tSkipped\n')
                tempF.close()

                print('\t----- restart -----\n')
                playback(token, tempF, multiplier)

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
                playback(token, tempF, multiplier)

        elif response['playing'] == False:

            # The music is not playing

            print('\tNo current playback')
            print('\tSleep: 10 s\n')

            time.sleep(10)

            multiplier += 0.5

            print('\t----- restart -----\n')
            playback(token, tempF, multiplier)

        else:

            print('\tFallback case.\n')

        if multiplier == 1.5:

            print('> Analyzing Playlists')

            playlists(token)

    # Call functions within playback()

    response = GETplayback(token, multiplier)
    duration(response, tempF, multiplier)

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

            verifyArtist()  Check if an artist's URI is in the file
            verifyTrack()   Check if a song's URI is under an artist's URI or search the entire file

            writeArtist()   Write the artist data to a file
            writeTrack()    Write the track data to a file

            popularity()    Adjust the popularity of a track + artist 
        '''

        def verifyArtist(path, artistURI):

            ''' verifyArtist() checks the contents of the json file path for the artist's URI
                The function returns the index of the artist if found and False bool if not

                ( str, str ) --> int **or bool

                ( path, artistURI ) --> int **or False

            '''

            with open(path) as fileRead:

                x = 0

                genreData = json.load(fileRead)

                for i in range(len(genreData['items'][0]['data'])):

                    if genreData['items'][0]['data'][i]['artist'][0]['URI'] == artistURI:

                        # Found the artist, return the index of the track

                        x = 0
                        return i 
                        break

                    else:
                        x += 1
                
                if x != 0:

                    # The artist was not found

                    return False

        def verifyTrack(path, trackURI, artistIndex):

            ''' verifyTrack() checks the contents of the json file path for the track's URI
                The function returns the index (int) of the track if found and False (bool) if not

                * To search through every song in the file (artist index not known) set artistIndex = False (bool)

                Artist index is known:
                    ( str, str, int ) --> index of track (int) or False if track not found (bool)

                Artist index is not known:
                    ( str, str, bool ) --> index of track (int) or False if track not found (bool)

                ( path, trackURI, artistIndex ) --> output described above

            '''

            # Search the entire file

            if type(artistIndex) == bool and artistIndex == False:

                # The artist index is not known, search through all songs in the file
                
                with open(path) as fileRead:

                    x = 0

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

                    x = 0

                    genreData = json.load(fileRead)

                    for i in range(len(genreData['items'][0]['data'][artistIndex]['artist'][0]['tracks'])):

                        if genreData['items'][0]['data'][artistIndex]['artist'][0]['tracks'][i]['track'][0]['URI'] == trackURI:

                            # Found the track, return the index of the track

                            x = 0
                            return i 
                            break

                        else:
                            x += 1
                    
                    if x != 0:

                        # The artist was not found

                        return False

        def writeArtist(path, artistName, artistURI):

            ''' writeSong() writes a new song with genreData's standard file structure when given all nessecary values 
            
                ( str, int, str, str, int ) --> write to file path

                ( path, artistIndex, trackName, trackURI, trackDuration )

                ** Newly written artist's will be located at index -1 (last)

                default values: 
                    popularity  : 1
                    genres      : []
                    tracks      : []

            '''
            with open(path) as fileRead: 

                genreData = json.load(fileRead)    

                genreData['items'][0]['data'].append(

                    { 'artist' : [
                        {   'name'      : artistName,
                            'URI'       : artistURI,
                            'popularity': 1,
                            'genres'    : [],
                            'tracks'    : [] 
                        }] 
                    })                      
            
                with open(path, 'r+') as fileWrite:

                    json.dump(genreData, fileWrite, indent=4) 

        def writeTrack(path, artistIndex, trackName, trackURI, trackDuration):

            ''' writeTrack() writes a new song with genreData's standard file structure when given all nessecary values 
            
                ( str, int, str, str, int ) --> write to file path

                ( path, artistIndex, trackName, trackURI, trackDuration )

                default values: 
                    popularity  : 1
                    exception   : False
                    genres      : Inherit parent's genres

            '''

            with open(path) as fileRead: 

                genreData = json.load(fileRead)    

                genreData['items'][0]['data'][artistIndex]['artist'][0]['tracks'].append(

                    { 'track' : [
                        {   'name'      : trackName,
                            'URI'       : trackURI,
                            'duration'  : trackDuration,
                            'popularity': 1,
                            'exception' : False,
                            'genres'    : genreData['items'][0]['data'][artistIndex]['artist'][0]['genres']
                        }] 
                    })                      
            
                with open(path, 'r+') as fileWrite:

                    json.dump(genreData, fileWrite, indent=4) 

        def popularity(path, artistIndex, trackIndex):

            ''' popularity() adjusts the popularity class of an Artist and Track within genreData.json

                ( str, str, str ) --> updated class

                ( path, artistIndex, trackIndex ) --> updated class

                ** If trackIndex is passed False (bool) the popularity will not be updated for the track
            '''

            with open(path) as fileRead:

                genreData = json.load(fileRead)

                genreData['items'][0]['data'][artistIndex]['artist'][0]['popularity'] += 1

                if trackIndex == type(int):

                    genreData['items'][0]['data'][artistIndex]['artist'][0]['tracks'][trackIndex]['track'][0]['popularity'] += 1

                with open(path, 'r+') as fileWrite:

                    json.dump(genreData, fileWrite, indent=4)

        path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\genreData.json'

        # Check if the artist is in the file

        x = verifyArtist(path=path, artistURI=response['artistURI'])

        if type(x) == int:

            # The artist index was found, x is the index, check if track is already under artist

            y = verifyTrack(path=path, artistIndex=x, trackURI=response['trackURI'])

            if type(y) == int:

                # The track index was found, no need to add the song, update the track + artist popularity

                popularity(path=path, artistIndex=x, trackIndex=y)

            if type(y) == bool:

                # The track index was not found, add the song, update the track + artist popularity

                writeTrack(path=path, artistIndex=x, trackName=response['trackName'], trackURI=response['trackURI'], trackDuration=response['trackDuration'])

                popularity(path=path, artistIndex=x, trackIndex=False)

        if type(x) == bool:

            # The artist index was not found, write the artist + track to the file

            writeArtist(path=path, artistName=response['artistName'], artistURI=response['artistURI'])

            writeTrack(path=path, artistIndex=-1, trackName=response['trackName'], trackURI=response['trackURI'], trackDuration=response['trackDuration'])

    # Call functions within localData()

    print('\t\t> Converting timestamp\n')
    response = convertTimestamp(response)

    print('\t\t> Writing listening history\n')
    path = writeHistory(response)

    print('\t\t> Sorting listeningData.json\n')
    sortHistory(path)

    print('\t\t> Checking genreData.json\n')
    checkLocalData(response)

def playlists(token):

    ''' playlists() GETs playlist data, compares it to local playlist data, 
        while making sure the execution is less than 20 seconds in order to 
        keep current with possible playback in the background
    ''' 

    def GETdisplayname(token):
        
        ''' GETdisplayname() GETs a user's current profile data in order to compare the display name
            to the owner of a playlist. This can be used to determine if the algorithm can manipulate 
            such a playlist

            ( token ) --> displayName

            https://developer.spotify.com/documentation/web-api/reference/users-profile/get-current-users-profile/
        '''
        
        url = 'https://api.spotify.com/v1/me'
        headers = {'Authorization': 'Bearer ' + token }

        response = requests.get(url, headers=headers, timeout=10)

        r = response.json()

        displayName = r ['display_name']

        return displayName

    def GETplaylists(token, displayName):

        ''' GETplaylists() uses a GET request to grab a user's playlist data and appends 
            the playlists name, id, and total amount of tracks to a list names 'playlists' 
            which is returned 

            ( str, str ) --> ( list ) --> [ [ playlist name, playlist id, total tracks on playlist ] ]

            ( token, displayName ) --> ( playlists ) --> [ [name, id, total], [], ... ] 

            https://developer.spotify.com/documentation/web-api/reference/playlists/get-a-list-of-current-users-playlists/
        '''

        # Retrieve the User's current playlists

        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {'Authorization': 'Bearer ' + token }
        params = { 'limit':50 }

        response = requests.get(url, headers=headers, params=params, timeout=10)

        # This GET request returns JSON including 50 of the user's playlists

        r = response.json()

        # Print status code 

        print('\tStatus: ', response.status_code)                                                                                
        print('\tProcessing request.\n')

        playlists = []
        x = 0

        for i in range( len(r['items'])):

            # Determine if the playlist is owned by the user

            if r['items'][i]['owner']['display_name'] == displayName:

                # Create list of needed data: playlist name, playlist ID, amount of tracks

                playlists.append( [r['items'][i]['name'], r['items'][i]['id'], r['items'][i]['tracks']['total']] )
                x += 1

        print('\t', i, 'playlists found')
        print('\t', x, 'playlists owned by', displayName, '\n')

        return playlists

    def updatePlaylists(token, playlists):

        ''' updatePlaylists() grabs each playlist owned by the user and checks whether
            or not the songs are in playlistData.json, adding or removing songs depending 
            on changes

            ( str, list ) --> ** various actions

            -- playlist: [[name, id, total songs], ..]

            https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlist/
        '''

        def GETplaylistByID( token, playlistID ):

            ''' GetplaylistByID() GETs all data pertaining to a specific playlist ID

                ( token ) --> json response

                https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlist/
            '''

        def localPlaylists( response ):

            ''' localPlaylists() locates the playlist by id locally and compares it to what 
                is in the response

                ( json response ) --> write to playlistData.json
            '''             

            path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\playlistData.json'                     

            p = json.load( open(path, 'r+') )

            playlistsWritten = 0
            songsWritten = 0

            for h in range(len(playlists)):

                x = 0

                for i in range(len(p["items"][0]['data'])):

                    # Open playlistData.JSON 

                    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\playlistData.json'                     
                    f = open(path, 'r+')
                    p = json.load(f)

                    # Format of playlists: playlist name, playlist ID, amount of tracks 

                    if p['items'][0]['data'][i]['playlist'][0]['id'] == playlists[h][1]:

                        # This playlist is already in playlistData.JSON, check songs and add song genres 

                        x = 0
                        break

                    else:

                        # This playlist is not in playlistData.JSON, add playlist, check songs and add song genres

                        x += 1 

            if x > 0:

                # Once a playlist is added, the file must be reopened

                print('\tWriting playlist', playlists[h][0])

                addPlaylist(path, playlists[h][1], playlists[h][2], playlists[h][0] )
                playlistsWritten += 1

                print('\t\tdone.\n')

                print('\tChecking songs:', playlists[h][0])

                checkPlaylistSongs(playlists[h][1], token, path)

                print('\n\t\t\tdone.\n')

            if x == 0:

                # Check songs

                print('\tChecking songs:', playlists[h][0])

                checkPlaylistSongs(playlists[h][1], token, path)

                print('\n\t\t\tdone.\n') 
                

            print('\n\t', playlistsWritten, 'playlists saved')
            print('\t', songsWritten, 'songs saved')\

        # Call functions within updatePlaylists()

        for i in range(len(playlists)):

            # For each playlist owned by the user

            response = GETplaylistByID( token, playlists[i][1] )   
            localPlaylists( response )

    # Call functions within playlists()

    displayName = spotify_requests.GETdisplayname(token)
    # displayName = GETdisplayname(token)
    playlists = GETplaylists(token, displayName)
    updatePlaylists(token, playlists)

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

    playback( tokenData['token'], tempF='', multiplier=0.0 )

# Call main

if __name__ == '__main__':
    main()

# TODO: Think about determining the different genres and checking if the artist and song data is added to genreData.json after something is added to listeningData.json as mentioned

# TODO: Create files / file error exceptions