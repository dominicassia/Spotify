# Dependencies
import requests
import json

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

        ( token, displayName ) --> ( playlists ) --> [ [name, id, total], [], ... ] 

        https://developer.spotify.com/documentation/web-api/reference/playlists/get-a-list-of-current-users-playlists/
    '''

    # Retrieve the User's current playlists

    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {'Authorization': 'Bearer ' + token }
    params = { 'limit':50 }

    response = requests.get(url, headers=headers, params=params, timeout=10)