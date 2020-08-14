''' 
Spotify Playlists
~~~~~~~~~~~~~~~~~~~~~

This module stores various functions for interacting between local json 
data and responses from the Spotify API.

============================

Functions:

    | localPlaylists( playlists )

'''

# Dependencies
import requests
import json

import spotify_requests as SR

#####################################################

def localPlaylists(playlists):

    ''' localPlaylists() locates the playlist by id locally and compares it to what 
        is in the response from spotify_requests.GETplaylistByID()

        ( list ) --> write to playlistData.json
    '''             

    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\playlistData.json'                     

    p = json.load( open(path, 'r+') )

    playlistsWritten = 0
    songsWritten = 0

    for h in range(len(playlists)):

        x = 0

        for i in range(len(p["items"][0]['data'])):

            # Open playlistData.JSON 

            f = open(path, 'r+')
            p = json.load(f)

            # Format of playlists: playlist name, playlist ID, amount of tracks 

            if p['items'][0]['data'][i]['playlist'][0]['id'] == playlists[h][1]:

                # This playlist is already in playlistData.JSON, check songs and add song genres 

                # Check songs in playlist
                checkPlaylistSongs(p['items'][0]['data'][i]['playlist'][0]['id'], token, path)

                # TODO: Add song genres

                x = 0
                break

            else:

                # This playlist is not in playlistData.JSON, add playlist, check songs and add song genres
                
                # Check songs in playlist
                checkPlaylistSongs(p['items'][0]['data'][i]['playlist'][0]['id'], token, path)

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

def addLocalplaylist(path, playlistID, playlistTrackNum, playlistName):
    ''' addLocalplaylist() adds a new playlist entry to the local json structure


        
    '''

    # Read the existing structure

    with open(path) as fileRead: 

        temp = json.load(fileRead)    

        # Append the new playlist

        temp['items'][0]['data'].append(
            { 
            "playlist":[
                {
                 "name":playlistName,
                 "id":playlistID,
                 "total-songs":playlistTrackNum,
                 "songs":[] 
                }] })                      
        
        # Write the playlist

        with open(path) as fileWrite:

            json.dump(temp, fileWrite, indent=4) 


def checkPlaylistSongs(playlistID, token, path):

    r = SR.GETplaylistByID(token, playlistID)

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
