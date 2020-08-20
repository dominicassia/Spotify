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

# Main functions

def localPlaylists(playlists, token):
    '''
        Compare Local Playlists to Response Playlists
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            This function locates the playlist by id (playlistData.json)
            and compares it to what is in the response from SR.GETplaylistByID()

            ( list, token ) = write to playlistData.json
    '''             

    # Initially open the file
    path = 'C:\\Users\\Domin\\github\\Python\\Spotify\\Data\\playlistData.json'                     

    p = json.load( open(path, 'r+') )

    playlistsWritten = 0
    songsWritten = 0

    print(playlists)

    # Length of playlists in the response
    for h in range(len(playlists)):

        x = 0

        # Length of playlists in playlistData.json
        for i in range(len(p["items"][0]['data'])):

            # Open playlistData.JSON 
            p = json.load(open(path, 'r+'))

            # If the local ID == response ID 
            if p['items'][0]['data'][i]['playlist'][0]['id'] == playlists[h][1]:

                # This playlist is already in playlistData.JSON, check songs and add song genres
                x = 0
                break

            else:

                # This playlist is not in playlistData.JSON, add playlist, check songs and add song genres
                x += 1 

    if x > 0:
        # Once a playlist is added, the file must be reopened

        # Add the playlist to playlistData
        print('\tWriting playlist', playlists[h][0])

        addPlaylist(path, playlists[h][1], playlists[h][2], playlists[h][0] )
            # Since the playlist was just appeneded it will be at index -1

        playlistsWritten += 1

        print('\t\tdone.\n')

        # Check songs in playlist
        print('\tChecking songs:', playlists[h][0])

        checkPlaylistSongs(-1, playlists[h][1], token, path)

        print('\n\t\t\tdone.\n')

        # Evaluate Genres
        print('\tEvaluating Genres:', playlists[h][0])

        # TODO: Add Genres

        print('\n\t\t\tdone.\n')
        
    if x == 0:

        # Check songs in playlist
        print('\tChecking songs:', playlists[h][0])
        checkPlaylistSongs(i, playlists[h][1], token, path)

        # TODO: Add Genres
        print('\tEvaluating Genres:', playlists[h][0])

        print('\n\t\t\tdone.\n') 
        
    print('\n\t', playlistsWritten, 'playlists saved')
    print('\t', songsWritten, 'songs saved')

def checkPlaylistSongs(index, playlistID, token, path):
    '''
        Check Songs in a Playlist
        ~~~~~~~~~~~~~~~~~~~~~~~~~
            This function GETs the playlist by ID and checks the songs
            returned in the response to what is in the json file. 

            - If a track from the response is not in the file, the track will be added to the file
            - If a track from the file is not in the response, the track will be removed from the file

            ( playlist ID, token, path ) = None
            ( str, str, str ) = None
    '''

    r = SR.GETplaylistTracks(token, playlistID)

    # Open playlistData.JSON as f and load keywords as obj. p
    
    with open(path, 'r+') as playlistData:

        p = json.load(playlistData)                                                                                

        # Find songs in response, but not in playlistData.JSON, add these songs to playlistData.JSON

        for g in range(len(r[1])):

            # Update / reppen file

            playlistData = open(path, 'r+')
            p = json.load(playlistData)

            x = 0

            # If there are no songs in the playlistData.JSON list, just add all the songs

            if len(p['items'][0]['data'][index]['playlist'][0]['songs']) > 0:

                for h in range(len(p['items'][0]['data'][index]['playlist'][0]['songs'])):

                    if r[1][g]['trackName'] == p['items'][0]['data'][index]['playlist'][0]['songs'][h]['name']:

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
                        index, 
                        r[1][g]['trackName'], 
                        r[1][g]['trackURI'], 
                        r[1][g]['artistName'], 
                        r[1][g]['artistURI']
                    )

            else: 
                # Add all songs to playlistData.JSON
                for k in range(len(r[1])):
                    addSongToPlaylistData(
                        path, 
                        index, 
                        r[1][k]['trackName'], 
                        r[1][k]['trackURI'], 
                        r[1][k]['artistName'], 
                        r[1][k]['artistURI']
                    )

        # Find songs not in response, but in playlistData.JSON, POST these songs to the online playlist

        tracksToAdd = []

        for i in range(len(p['items'][0]['data'][index]['playlist'][0]['songs'])):

            # Update / reopen file

            playlistData = open(path, 'r+')
            p = json.load(playlistData)

            y = 0

            for j in range(len(r[1])):

                if p['items'][0]['data'][index]['playlist'][0]['songs'][i]['URI'] == r[1][j]['trackURI']:

                    # The song from playlistData.JSON is in the public playlist, no action

                    y = 0 
                    break

                else:

                    # The song in playlistData.JSON is not in the public playlist, add it by appending to list of songs to add

                    y += 1
            
            if y > 0:

                print('\t\tAdding track:', p['items'][0]['data'][index]['playlist'][0]['songs'][i]['name'])

                tracksToAdd.append(p['items'][0]['data'][index]['playlist'][0]['songs'][i]['URI'])

        if len(tracksToAdd) > 0:    
            SR.postPlaylist(token, p['items'][0]['data'][index]['playlist'][0]['id'], tracksToAdd)

# Sub Functions

def addLocalplaylist(path, id, totalTracks, name):
    ''' 
        Add a Playlist to a Local Json File
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This function adds a new playlist entry to the local json structure

            ( file path, playlist id, total tracks, playlist name ) = None
            ( str, str, int, str ) = None
    '''

    # Read the existing structure

    with open(path) as fileRead: 

        temp = json.load(fileRead)    

        # Append the new playlist

        temp['items'][0]['data'].append(
            { 
            "playlist":[
                {
                    "name":        name,
                    "id":          id,
                    "total-songs": totalTracks,
                    "songs":       [] 
                }]
            })                      
        
        # Write the playlist

        with open(path) as fileWrite:

            json.dump(temp, fileWrite, indent=4) 

def addSongToPlaylistData(path, index, trackName, trackURI, artistName, artistURI):

    print('\t\tWriting', trackName )

    # Read existing data
    with open(path) as fileRead:
        playlistData = json.load(fileRead)

        # Append new data
        playlistData['items'][0]['data'][index]['playlist'][0]['songs'].append(
            {
                "name":     trackName,
                "URI":      trackURI,
                "artist": [
                    {
                        "name": artistName,
                        "URI":  artistURI
                    }]
            })

        # Write new structure
        with open(path, 'r+') as fileWrite:
            json.dump(playlistData, fileWrite, indent=4)

    print('\t\t\tdone.')

