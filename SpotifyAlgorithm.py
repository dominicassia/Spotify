# Libraries
import base64               # Encode
import urllib.parse         # Encode
import requests             # cURL 
import json                 # Parse
import time                 # Execution time
import datetime             # Sorting timestamps
import operator             # Sorting specific indices
import functools            # Caching

#####################################################

def clientInfo():

    # Grab client data from tokenData.JSON return to variables in main

    # Retrieve the saved token

    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\tokenData.json'

    with open(path, 'r') as t:                                          # Open tokenData.json
        temp = json.load(t)                                             # Load as object

        token = temp['data'][0]['token']                                 
        clientID = temp['data'][0]['clientID']  
        clientSecret = temp['data'][0]['clientSecret']    
        userID = temp['data'][0]['clientUserID']   
        refreshToken = temp['data'][0]['refreshToken']  
        redirectURI = temp['data'][0]['redirectURI']  

        return token, refreshToken, clientID, clientSecret, userID, path, redirectURI

def validate(token, refreshToken, path, userID, clientID, clientSecret):

    temp = userInfo(token, userID)
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

    response = requests.get(url=url, headers=headers, timeout=10)

    return response

def authURL(clientID, redirectURI):
    
    # Encode

    # authorizationE = base64.b64encode( str(clientID + ':' + clientSeceret).encode('ascii'))
    authorizationE = 'MTllZWNiMzM1Y2M4NDg5OWI0YmMwMDZkOWVkZjM4ZDE6NTE1MWFjMzdlYmYzNDg5MTk5ZTVhNWY1MTkwZjZmNGQ='
    redirectURIE = urllib.parse.quote_plus(redirectURI)

    scopes = 'user-read-playback-state%20user-modify-playback-state%20user-read-currently-playing%20user-read-email%20user-read-private%20playlist-read-collaborative%20playlist-modify-public%20playlist-read-private%20playlist-modify-private%20user-library-modify%20user-library-read%20user-top-read%20user-read-recently-played%20user-follow-read%20user-follow-modify'

    # Assemble
    authorizationURL = 'https://accounts.spotify.com/authorize?' + 'client_id=' + clientID + '&scope=' + scopes + '&response_type=code&redirect_uri=' + redirectURIE

    return authorizationURL

def refresh(refreshToken, clientID, clientSecret):
    
    data = { 'grant_type': 'refresh_token', 'refresh_token': refreshToken }

    response = requests.post('https://accounts.spotify.com/api/token', data=data, auth=(clientID, clientSecret), timeout=10)
    
    # This POST returns JSON with the new access token
    
    r = response.json()

    print('\tNew token obtained.')
    return r['access_token']


def recentlyPlayed(token):

    # https://developer.spotify.com/documentation/web-api/reference/player/get-recently-played/

    url = 'https://api.spotify.com/v1/me/player/recently-played'
    headers = { 'Authorization':'Bearer ' + token }                                                     
    params = { 'limit':50 }

    response = requests.get(url, headers=headers, params=params, timeout=10)                                        # GET request

    # This GET returns JSON with the User's last played 50 songs 

    print('\tStatus: ', response.status_code)                                                   
    print('\tProcessing request.\n')

    r = json.loads(str(response.text))
   
    artistsWritten = 0                                                                             
    songsWritten = 0

    for h in range( len(r['items']) ):        
        
        x = 0

        # Open genreData.JSON as genreData object

        path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\genreData.json'
        f = open(path, 'r')                                                                       
        genreData = json.load(f)

        for i in range(len(genreData['items'][0]['data'])):                                                      

            if str(r['items'][h]['track']['artists'][0]['name']) == str(genreData['items'][0]['data'][i]['artist'][0]['name']):

                # If the Artist in the response is already in the file, x = 0, check if the response song is already in the file
                               
                x = 0
                break

            elif str(r['items'][h]['track']['artists'][0]['name']) != str(genreData['items'][0]['data'][i]['artist'][0]['name']):
               
                # If the Artist in the response is not in the file, x > 0, add the artist and the response song 

                x += 1

        if x > 0:

            # Add the response Artist and correlating song

            print('\tWriting Artist: ', r['items'][h]['track']['artists'][0]['name'])

            addArtist(path, r['items'][h]['track']['artists'][0]['name'], r['items'][h]['track']['artists'][0]['uri'])
            artistsWritten += 1
            
            print('\t\tdone.\n')

            # The last added Artist is at index -1, add the correlating song to that index

            print('\tWriting Song: ', r['items'][h]['track']['name'])

            addSong(path, -1, r['items'][h]['track']['name'], r['items'][h]['track']['uri'], r['items'][h]['track']['duration_ms'])
            songsWritten += 1

            print('\t\tdone.\n')

        if x == 0:

            # Find the response Artist's index within genreData.JSON, check if the reponse song is already in the file

            for u in range( len(genreData['items'][0]['data']) ):

                if r['items'][h]['track']['artists'][0]['name'] == genreData['items'][0]['data'][u]['artist'][0]['name']:

                    index = u
                    break

            y = 0

            for o in range( len(genreData['items'][0]['data'][index]['artist'][0]['songs']) ):

                # Iterate through all songs the Artsit's file

                if r['items'][h]['track']['name'] == genreData['items'][0]['data'][index]['artist'][0]['songs'][o]['song'][0]['name']:

                    # If song is found, y = 0, no song to add

                    y = 0
                    break
                
                else:

                    # If the song is not found, y > 0, add the song

                    y += 1

            if y > 0:

                # Add the song

                print('\tWriting Song: {song} to {artist}'.format(song=r['items'][h]['track']['name'], artist=genreData['items'][0]['data'][index]['artist'][0]['name']) )

                addSong(path, index, r['items'][h]['track']['name'], r['items'][h]['track']['uri'], r['items'][h]['track']['duration_ms'])
                songsWritten += 1

                print('\t\tdone.\n')

    print('\t', artistsWritten, 'artists written')
    print('\t', songsWritten, 'songs written')

    return genreData, response

def listeningHistory(response):
    
    # https://developer.spotify.com/documentation/web-api/reference/player/get-recently-played/

    print('\tProcessing request.\n')

    r = json.loads(response.text)

    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\listeningData.json'

    with open(path, 'r+') as fileAppend:

        listeningData = json.load(fileAppend)

        songsWritten = 0

        # List format: [timestamp, name, uri]

        lst = []

        # Add existing data from file into list

        for e in range(len(listeningData['items'][0]['data'])):

            lst.append([
                listeningData['items'][0]['data'][e][0]['timestamp'],
                listeningData['items'][0]['data'][e][0]['name'],
                listeningData['items'][0]['data'][e][0]['URI']
                ])

        # Add new songs from response into list

        for f in range(len(r['items'])):

            lst.append([
                r['items'][f]['played_at'],
                r['items'][f]['track']['name'],
                r['items'][f]['track']['uri']
                ])

            # Modify newly added timestamps to match that of the file for comparison
                # playedAt: [ [ [ 'YYYY' , 'MM' , 'DD' ] , [ 'HH' , 'MM' , 'SS' ], uri, name ] ], ...
                    
            lst[-1][0] = lst[-1][0].split('T')                        # ['2001-06-05T02:44:50.540Z', 'initial', 'generic_URI']

            lst[-1][0][0] = lst[-1][0][0].split('-')                  # [['2001-06-05', '02:44:50.540Z'], 'initial', 'generic_URI']

            lst[-1][0][1] = lst[-1][0][1].split(':')                  # [[['2001', '06', '05'], '02:44:50.540Z'], 'initial', 'generic_URI']

            lst[-1][0][1][2] = lst[-1][0][1][2][:-1]                  # [[['2001', '06', '05'], ['02', '44', '50.540Z']], 'initial', 'generic_URI']

            lst[-1][0][1][2] = lst[-1][0][1][2].split('.')            # [[['2001', '06', '05'], ['02', '44', '50.540']], 'initial', 'generic_URI']

                # [[[['2001', '06', '05'], ['02', '44', ['50', '540']]], 'initial', 'generic_URI']

            lst[-1][0] = '{year} {month} {day} {hour} {minute} {second} {microsecond}'.format(year=lst[-1][0][0][0], month=lst[-1][0][0][1], day=lst[-1][0][0][2], hour=lst[-1][0][1][0], minute=lst[-1][0][1][1], second=lst[-1][0][1][2][0], microsecond=lst[-1][0][1][2][0])

                # ['2001-06-05 02:44:50.500000', 'initial', 'generic_URI']

            lst[-1][0] = datetime.datetime.strptime(lst[-1][0], '%Y %m %d %H %M %S %f')    

        # Compare timestamps

        for h in range(len(lst)):

            x = 0

            fileAppend = open(path, 'r+')
            listeningData = json.load(fileAppend)

            for i in range(len(listeningData['items'][0]['data'])):

                # Manip then check

                if str(lst[h][0]) == str(listeningData['items'][0]['data'][i][0]['timestamp']):

                    # The timestamp is already in the file, do nothing
                    x = 0
                    break
                
                else:

                    # The timestamp is not in the file, add the timestamp and correlating data
                    x += 1

            if x > 0:

                # The timestamp is not in the file, add the timestamp and correlating data

                print('\tWriting', lst[h][1])

                addTimestamp(path, str(lst[h][0]), lst[h][1], lst[h][2] )
                songsWritten += 1

                print('\t\tdone.\n')

    print('\tSorting.')

    with open(path) as fileRead: 

        temp = json.load(fileRead) 

        lst = []

        for t in range(len(temp['items'][0]['data'])):

            lst.append( [ temp['items'][0]['data'][t][0]['timestamp'], temp['items'][0]['data'][t][0]['name'], temp['items'][0]['data'][t][0]['URI'] ] )            

        # lst:  [ timestamp, name, uri ] to lst [ [ ['YYYY','MM','DD'] , ['HH','MM','SS'] ], name, uri ]

        # Sort list
            # https://stackoverflow.com/questions/4174941/how-to-sort-a-list-of-lists-by-a-specific-index-of-the-inner-list

        lst = sorted( lst, key=operator.itemgetter(0) )

        # Reassign

        for j in range(len(lst)):

            lst[j] = [{'timestamp':str(lst[j][0]), 'name':lst[j][1], 'URI':lst[j][2]}]

        temp['items'][0]['data'] = lst

        # Write

        fileWrite = open(path, 'r+')
        json.dump(temp, fileWrite, indent=4) 
        fileWrite.close()

    print('\t\tdone.')

    print('\n\tCalculating popularity.')

    adjusted = popularity()

    print('\t\tdone.')

    print('\n\t', songsWritten, 'songs written')
    print('\n\t', adjusted, 'popularity classes adjusted')

def popularity():

    # If a song is added to the listening history, add 1 to the popularity of that song within genre data

    path1 = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\listeningData.json'                     

    with open(path1) as fileRead:

        listeningData = json.load(fileRead)

        # Find the index of the timestamp checked last

        for i in range(len(listeningData['items'][0]['data'])):

            if listeningData['items'][0]['popularity'][0]['timestamp'] == listeningData['items'][0]['data'][i][0]['timestamp']:

                break

        # Find the song in genreData.json and add one to 'popularity'

        path2 = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\genreData.json'  

        # Start at last index + 1 and go for the remaining length of songs not adjusted with 

        for j in range(i + 1, len(listeningData['items'][0]['data'])):

            # Open genreData.json to read from

            with open(path2) as genreDataRead:

                genreDataR = json.load(genreDataRead)

                # Find the index of the song were adding to 

                for k in range(len(genreDataR['items'][0]['data'])):

                    for l in range(len(genreDataR['items'][0]['data'][k]['artist'][0]['songs'])):

                        # Find song by URI

                        if listeningData['items'][0]['data'][j][0]['URI'] == genreDataR['items'][0]['data'][k]['artist'][0]['songs'][l]['song'][0]['URI']:

                            # Get current value of popularity of song and add one

                            genreDataR['items'][0]['data'][k]['artist'][0]['songs'][l]['song'][0]['popularity'] += 1

                            # Get current value of popularity of artist and add one

                            genreDataR['items'][0]['data'][k]['artist'][0]['popularity'] += 1
         
                # Open genreData.json to read from   

                with open(path2, 'w') as genreDataWrite:

                    # Place the new popularity integers in genreData.json

                    json.dump(genreDataR, genreDataWrite, indent=4)     

        # Update the timestamp at at the top of listeningData.json

        # Assign last checked timestamp to the popularity class for next time

        try:
            listeningData['items'][0]['popularity'][0]['timestamp'] = listeningData['items'][0]['data'][j][0]['timestamp']
        
            with open(path1, 'w') as fileWrite:

                json.dump(listeningData, fileWrite, indent=4)

                return j

        except UnboundLocalError:

            return 0

def addTimestamp(path, timeStamp, trackName, trackURI):

    with open(path) as fileRead:
        listeningData = json.load(fileRead)

        lst = [{
            'timestamp':timeStamp,
            'name':trackName,
            'URI':trackURI
        }]

        listeningData['items'][0]['data'].append(lst)

        fileWrite = open(path, 'r+')                  
        json.dump(listeningData, fileWrite, indent=4) 
        fileWrite.close()

def addArtist(path, trackName, trackURI):
    
    with open(path, 'r+') as f: 
        genreData = json.load(f)    
        genreData['items'][0]['data'].append(
            { 'artist':[
                {   'name':trackName,
                    'genres':[],
                    'URI':trackURI,
                    'popularity':1,
                    'songs':[] 
                }] 
            })                      
        
        fileWrite = open(path, 'r+') 
        json.dump(genreData, fileWrite, indent=4) 
        fileWrite.close()

def addSong(path, index, trackName, trackURI, trackDuration):

    with open(path, 'r+') as f: 
        genreData = json.load(f)
        genreData['items'][0]['data'][index]['artist'][0]['songs'].append( 
            { 'song': [
                {   'name':trackName, 
                    'URI':trackURI, 
                    'exception':False, 
                    'genres': genreData['items'][0]['data'][index]['artist'][0]['genres'], 
                    'duration':trackDuration, 
                    'popularity':1 
                }] 
            } )                      
        
        fileWrite = open(path, 'r+') 
        json.dump(genreData, fileWrite, indent=4) 
        fileWrite.close()

def updateGenres():

    # Create a list of all genres at the beginning of the genreData.json file

    print('\tChecking.')

    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\genreData.json'                     
    f = open(path, 'r+')
    genreData = json.load(f)

    genreChecked = 0
    genreWritten = 0

    for h in range(len(genreData['items'][0]['genres'])):

        for i in range(len(genreData['items'][0]['data'])):

            x = 0

            for j in range(len(genreData['items'][0]['data'][i]['artist'][0]['genres'])):

                if genreData['items'][0]['data'][i]['artist'][0]['genres'][j] == genreData['items'][0]['genres'][h]:

                    # The genre is already in there, do nothing

                    x = 0
                    genreChecked += 1
                    break

                else:

                    # The genre is not there, add the genre

                    x += 1
                    genreChecked += 1

            if x > 0:

                # Write the genre

                for k in range(len(genreData['items'][0]['genres'])):

                    u = 0

                    if genreData['items'][0]['genres'][k] == genreData['items'][0]['data'][i]['artist'][0]['genres'][j]:

                        u = 0 
                        break

                    else:

                        u += 1

                if u > 0:
                    
                    print('\n\tWriting genre:', genreData['items'][0]['data'][i]['artist'][0]['genres'][j])

                    f.close()
                    addGenre(path, genreData['items'][0]['data'][i]['artist'][0]['genres'][j])
                    genreWritten += 1

                    # Open genreData.JSON again to update information

                    f = open(path, 'r+')
                    genreData = json.load(f)
                    print('\t\tdone.')

    print('\tSorting.')

    # Alphabetically sort the genres

    with open(path) as fileRead: 
        temp = json.load(fileRead) 

        lst = temp['items'][0]['genres']
        lst.sort()
        temp['items'][0]['genres'] = lst

        fileWrite = open(path, 'r+')
        json.dump(temp, fileWrite, indent=4) 
        fileWrite.close()

    print('\n\t', genreWritten, 'genres written')
    print('\t', genreChecked, 'genres checked')

def addGenre(path, genre):

    # Add the genre to main genre list

    with open(path) as fileRead: 
        temp = json.load(fileRead)
        
        temp['items'][0]['genres'].append(genre)   

        fileWrite = open(path, 'r+')                  
        json.dump(temp, fileWrite, indent=4) 
        fileWrite.close()


def currentPlaylists(token, displayName):

    # Retrieve the User's current playlists

    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {'Authorization': 'Bearer ' + token }
    params = { 'limit':50 }

    response = requests.get(url, headers=headers, params=params, timeout=10)

    # This GET request returns JSON including 50 of the user's playlists

    r = response.json()

    print('\tStatus: ', response.status_code)                               # Print status code                                                   
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
    print('\t', x, 'playlists owned by', displayName)

    return playlists

def updatePlaylists(token, playlists):

    print('\tChecking.\n')

    # Initially open playlistData.JSON 

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
    print('\t', songsWritten, 'songs saved')

def checkPlaylistSongs(playlistID, token, path):

    # https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/

    url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id = playlistID)
    headers = { 'Authorization':'Bearer ' + token }                                                     
    params = { 'limit':100 }

    response = requests.get(url=url, headers=headers, params=params, timeout=10)

    # This GET returns JSON with all track data from the playlist ID given

    print('\t\tStatus: ', response.status_code)                                                   
    print('\t\tProcessing request.\n')

    r = json.loads(str(response.text))

    # Open playlistData.JSON as f and load keywords as obj. p

    with open(path, 'r+') as playlistData:
        p = json.load(playlistData)                                                                                

        # Find the index of the given playlist ID within playlistData.JSON, assign to playlistIndex

        for e in range(len(p['items'][0]['data'])):                                                     

            if playlistID == p['items'][0]['data'][e]['playlist'][0]['id']:
                playlistIndex = e
                break

        # Find songs in response, but not in playlistData.JSON, add these songs to playlistData.JSON

        for g in range(len(r['items'])):

            # Update / reppen file

            playlistData = open(path, 'r+')
            p = json.load(playlistData)

            x = 0

            # If there are no songs in the playlistData.JSON list, just add all the songs

            if len(p['items'][0]['data'][playlistIndex]['playlist'][0]['songs']) > 0:

                for h in range(len(p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'])):

                    if r['items'][g]['track']['name'] == p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'][h]['name']:

                        # The song is already in the file, do nothing
                        x = 0
                        break

                    else:

                        # The song is not found in the file, add the song
                        x += 1

                if x > 0:

                    # Add the song to playlistData.JSON

                    addSongToPlaylistData(
                        path, 
                        playlistIndex, 
                        r['items'][g]['track']['name'], 
                        r['items'][g]['track']['uri'], 
                        r['items'][g]['track']['artists'][0]['name'], 
                        r['items'][g]['track']['artists'][0]['uri'])

            else: 

                # Add the song to playlistData.JSON

                addSongToPlaylistData(
                    path, 
                    playlistIndex, 
                    r['items'][g]['track']['name'], 
                    r['items'][g]['track']['uri'], 
                    r['items'][g]['track']['artists'][0]['name'], 
                    r['items'][g]['track']['artists'][0]['uri'])

        # Find songs not in response, but in playlistData.JSON, POST these songs to the online playlist

        tracksToAdd = []

        for i in range(len(p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'])):

            # Update / reopen file

            playlistData = open(path, 'r+')
            p = json.load(playlistData)

            y = 0

            for j in range(len(r['items'])):

                # print( p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'][i]['name'], '==', r['items'][j]['track']['name'] )

                if p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'][i]['name'] == r['items'][j]['track']['name']:

                    # The song from playlistData.JSON is in the public playlist, no action

                    y = 0 
                    break

                else:

                    # The song in playlistData.JSON is not in the public playlist, add it by appending to list of songs to add

                    y += 1

            
            if y > 0:

                print('\t\tAdding track:', p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'][i]['name'])

                tracksToAdd.append(p['items'][0]['data'][playlistIndex]['playlist'][0]['songs'][i]['URI'])

        if len(tracksToAdd) > 0:    
            postPlaylist(token, p['items'][0]['data'][playlistIndex]['playlist'][0]['id'], tracksToAdd)

def addSongToPlaylistData(path, playlistIndex, trackName, trackURI, artistName, artistURI):

    print('\t\tWriting', trackName )

    with open(path) as fileRead:
        playlistData = json.load(fileRead)

        playlistData['items'][0]['data'][playlistIndex]['playlist'][0]['songs'].append({
            "name":trackName,
            "URI":trackURI,
            "artist": [{
                "name":artistName,
                "URI":artistURI
            }]
        })

        with open(path, 'r+') as fileWrite:
            json.dump(playlistData, fileWrite, indent=4)

    print('\t\t\tdone.')

def postPlaylist(token, playlistID, tracksToAdd):

    print('\t\tPosting tracks.')

    # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/

    uris = ''
    for i in range(len(tracksToAdd)):
        uris += tracksToAdd[i]

    url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'.format(playlist_id = playlistID)
    headers = {'Authorization': 'Bearer ' + token }
    params = { 'uris':uris }

    response = requests.post(url, headers=headers, params=params, timeout=10)

    # This POST returns a 'snapshot_id' of the action taken

    print('\t\tStatus:', response.status_code)
    print('\t\t\tdone.\n')

def addSongPlaylist(path, index, track):
    with open(path) as f: 
        playlist = json.load(f)    
        playlist['items'][0]['data'][index]['playlist'][0]['songs'].append(track)                      
        fw = open(path,'r+') 
        json.dump(playlist, fw, indent=4) 
        fw.close()

def addPlaylist(path, playlistID, playlistTrackNum, playlistName):
    with open(path) as f: 
        temp = json.load(f)    

        temp['items'][0]['data'].append({ "playlist":[{ "name":playlistName, "id":playlistID, "total-songs":playlistTrackNum, "songs":[] }] })                      
        
        fw = open(path,'r+') 
        json.dump(temp, fw, indent=4) 
        fw.close()

def createPlaylist(token, playlistName, songs, userID):

    print('\tCreating playlist.')

    url = 'https://api.spotify.com/v1/users/'+ userID +'/playlists'
    headers = {'Authoriation': 'Bearer {token}'.format(token=token), 'Content-Type': 'application/json' }
    params = { 'name':playlistName }

    requests.post(url, headers=headers, params=params, timeout=10)

    print('\t\tdone.\n')  


def durationListened(token):

    # https://developer.spotify.com/documentation/web-api/reference/player/get-information-about-the-users-current-playback/

    url = 'https://api.spotify.com/v1/me/player'
    headers = {'Authorization': 'Bearer ' + token }

    try:
        response = requests.get(url=url, headers=headers, timeout=10)

        # This GET request returns information about a user's current listening status

    except TimeoutError:

        print('timeout error.')
        durationListened(token)

    print('\tStatus: ', response.status_code)

    # Unauthorized

    if response.status_code == 401:
        print('- Unauthoorized')
        time.sleep(10)
        durationListened(token)

    # No new data to grab

    if response.status_code == 204:
        print('- Nothing is playing ( no data / waiting 20s )')
        time.sleep(20)
        durationListened(token)

    print(response.text)        # Delete

    r = json.loads(str(response.text))    

    # Assign
    
    trackName = r['item']['name'] 
    trackURI = r['item']['uri']
    trackProgress = r['progress_ms']
    trackDuration = r['item']['duration_ms']
    artistName = r['item']['artists'][0]['name']
    artistURI = r['item']['artists'][0]['uri']

    # Functions

    def moreThanHalf(duration, progress):
        if progress > (int(duration / 2)):
            return True
        else:
            return False

    def constantChecker():

        # Constantly check for what is being listened to, if the user listens to more than half the song without switching it, it can be added to listening history for analysis

        if r['is_playing'] == True:

            if moreThanHalf(trackDuration, trackProgress) == True and trackURI == tempURI:

                # Add to listening history / proceed with script
                print('- More than half of the same song has been listened to ( adding to history )')
                pass

            else:

                # Calculate and wait for the remainder of half the song
                print('- Less than half the song has been listened to ( waiting', int(int(trackDuration / 2) - trackProgress) / 1000,'s )')

                tempURI = trackURI
                time.sleep( int(int(trackDuration / 2) - trackProgress) / 1000 )
                durationListened(token)

        elif r['is_playing'] == False:

            # The music is not playing

            print('- Nothing is playing ( no data / waiting 10s )')
            time.sleep(10)
            durationListened(token)

    # Call function

    print(r['is_playing'])

    constantChecker()
    

def playback(token):

    # Monitor the User's playback to determine which songs are important

    def GETplayback(token):

        # https://developer.spotify.com/documentation/web-api/reference/player/get-information-about-the-users-current-playback/

        url = 'https://api.spotify.com/v1/me/player'
        headers = {'Authorization': 'Bearer ' + token }

        try:
            response = requests.get(url=url, headers=headers, timeout=10)

            # This GET request returns information about a user's current listening status

        except TimeoutError:

            print('timeout error.')
            durationListened(token)

        print('\tStatus: ', response.status_code)

        # Unauthorized

        if response.status_code == 401:
            print('- Unauthoorized')
            time.sleep(10)
            durationListened(token)

        # No new data to grab

        if response.status_code == 204:
            print('- Nothing is playing ( no data / waiting 20s )')
            time.sleep(20)
            durationListened(token)

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
    
    def moreThanHalf(duration, progress):

        if progress > (int(duration / 2)):

            return True
            
        else:

            return False

    def duration(response):

        if response['playing'] == True:

            if moreThanHalf( response['trackDuration'], response['trackProgress'] ) == True and trackURI == tempURI:

                # More than half of the same song has been listened to, add to listening history

                print('- More than half of the same song has been listened to ( adding to history )')

            elif moreThanHalf( response['trackDuration'], response['trackProgress'] ) == False:

                # Calculate and wait for the remainder of half the song

                print('- Less than half the song has been listened to ( waiting', int(int(response['trackDuration'] / 2) - response['trackProgress']) / 1000,'s )')

                time.sleep( int(int(response['trackDuration'] / 2) - response['trackProgress']) / 1000 )
                duration(response)

            elif trackURI != tempURI:

                # The User skipped the song before getting halfway, restart the function

                playback(token)

        elif response['playing'] == False:

            # The music is not playing

            print('- Nothing is playing ( no data / waiting 10s )')
            time.sleep(10)
            playback(token)

    # Call functions

    response = GETplayback(token)
    duration(response)

def exeuctionTime(tStart):
    tEnd = time.time()                                                      # End Clock
    exTime = round(tEnd-tStart, 4)                                          # Calculate execution & round execution time
    print('\tExecuted in', exTime, 's.\n') 

def main():

    print('\n')   

    # Extract client / token information
    tStart = time.time()

    print('> Extracting data.')
    token, refreshToken, clientID, clientSecret, userID, path, redirectURI = clientInfo()
    
    exeuctionTime(tStart)

    # Verifying token
    tStart = time.time()

    print('> Verifying token.')
    token, displayName = validate(token, refreshToken, path, userID, clientID, clientSecret)
    
    exeuctionTime(tStart)

    # Monitor playback

    playback(token)









    # Recently played
    tStart = time.time()

    print('> Retrieving recently played songs.')
    genre, recentlyPlayedResponse = recentlyPlayed(token)

    exeuctionTime(tStart)

    # Write recently played songs to listenHistory
    tStart = time.time()

    print('> Writing listening history.')                            
    listeningHistory(recentlyPlayedResponse)

    exeuctionTime(tStart)

    # Update genres
    tStart = time.time()

    print('> Updating genres.')
    updateGenres()                                                          

    exeuctionTime(tStart)

    # Grab list of playlists/needed data
    tStart = time.time()

    print('> Retrieving Playlists.')
    playlists = currentPlaylists(token, displayName)

    exeuctionTime(tStart)

    # Update playlists
    tStart = time.time()

    print('> Updating Playlists.')
    updatePlaylists(token, playlists)

    exeuctionTime(tStart)

    # Duration listened

    durationListened(token)

main()

# Continuously run

# while True:
#     main()
#     time.sleep(3600)


'''
** todo functions:

    isLiked():      check if a song from the response is liked --> pull all liked songs and compare to songs attempting to be added

    durationListened():     if duration listened to a song is less than 45 sec, don't add to genreData

    similarSongs():     songs listened to before and after a track will give insight to what genre that song may be --> if a un-genred song is surrounded by the same genres x amount of time, guess that that song is that genre
        nearbySongs():      find songs that have been played "around" a track and comapre their genres   songL --> songC --> songR, determine songC's genre by L & R genre

    dirCheck():     ensure there are data files to write to, if not create them with the generic format

Ideal script:
    - Verify the token is valid
    - Constantly monitors what youre listening to, in order to understand how long you've listened to a song
    - If more than half the song is listened to, add it to listening history
    - Add listening history songs to genreData.json
        - Get additional data needed from pulling user's recently played songs and navigating backwards to find song
    - Check playlists over a certain interval of time

'''

