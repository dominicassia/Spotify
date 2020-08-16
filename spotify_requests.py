''' 
Spotify Requests
~~~~~~~~~~~~~~~~~~~~~

This module stores various functions for interacting between the Spotify API 
and the algorithm using the requests library.

============================

Functions:

    | GETdisplayname( token )
    | GETplaylists( token, displayName )
    | GETplaylistByID( token, playlistID )
    | GETplaylistTracks( token, playlistID )
    | GETplayback( token, multiplier )

'''

# Dependencies
import requests
import json
import time

#####################################################

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

    displayName = r['display_name']

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

            playlists.append([
                r['items'][i]['name'], 
                r['items'][i]['id'], 
                r['items'][i]['tracks']['total']
                ])
                
            x += 1

    print('\t', i, 'playlists found')
    print('\t', x, 'playlists owned by', displayName, '\n')

    return playlists

def GETplaylistByID(token, playlistID):

    ''' GETplaylistByID() GETs all data pertaining to a specific playlist ID

        ( token ) --> json response

        https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlist/
    '''

    url = 'https://api.spotify.com/v1/playlists/{playlist_id}'.format(playlist_id = playlistID)
    headers = { 'Authorization':'Bearer ' + token }                                                     

    response = requests.get(url=url, headers=headers, timeout=10)

    # This GET returns JSON with all track data from the playlist ID given

    print('\t\tStatus: ', response.status_code)                                                   
    print('\t\tProcessing request.\n')

    r = json.loads(str(response.text))

    return r

def GETplaylistTracks(token, playlistID):
    
    ''' 
        GET Request a Playlist's Tracks
        ~~~~~~~~~~~~~~~~
            This function GETs all tracks in a playlist when given the playlist's ID

            ( token, playlist ID ) = list
            ( str, str ) = list

            list = [ playlistID, [{trackName, trackURI, trackDuration, artistName, artistURI}, {...}, ... ]]


        Reference: https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/
    '''

    url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id = playlistID)
    headers = { 'Authorization':'Bearer ' + token }                                                     
    params = { 'limit':100 }

    # This GET returns JSON with all track data from the playlist ID given
    response = requests.get(url=url, headers=headers, params=params, timeout=10)

    print('\t\tStatus: ', response.status_code)                                                   
    print('\t\tProcessing request.\n')

    r = json.loads(str(response.text))

    # Structure of plystRespData:
    # [ playlistID, [{trackName, trackURI, trackDuration, artistName, artistURI}, {...}, ... ]]

    plystRespData = []
    temp = []

    plystRespData.append(playlistID)
    plystRespData.append(temp)

    for i in range(r['total']):

        # Data kept from http response
        plystRespData[1].append(
            {
                'trackName'       : '',
                'trackURI'        : '',
                'trackDuration'   : '',
                'artistName'      : '',
                'artistURI'       : '',
            })

    return plystRespData

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
