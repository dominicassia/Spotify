# Dependencies
import requests
import json

#####################################################

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
    print('\t', songsWritten, 'songs saved')
