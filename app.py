'''
This code was based on these repositories:
    https://github.com/datademofun/spotify-flask
    https://github.com/drshrey/spotify-flask-auth-example
    https://github.com/mari-linhares/spotify-flask
'''

from flask import Flask, request, redirect, g, render_template, session
from spotify_requests import spotify


app = Flask(__name__)
app.secret_key = 'some key for session'

# ----------------------- AUTH API PROCEDURE -------------------------

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)

@app.route("/sendFilter", methods = ['POST'])
def sendFilter():
    session['max_input'] = request.form['max_input']
    session['min_input'] = request.form['min_input']

    return redirect('startFilter')


@app.route("/startFilter/")
def startFilter():
    if 'auth_header' in session and 'playlist_id' in session:
        max_tempo = float(session['max_input'])
        min_tempo = float(session['min_input'])
        auth_header = session['auth_header']
        playlist_id = session['playlist_id']
        # get profile data
        profile_data = spotify.get_users_profile(auth_header)

        playlist_tracks = spotify.get_playlist_tracks(auth_header, playlist_id)

        offset = 100
        #pages > 100 elements
        while playlist_tracks['next'] != None:
            offset += 100
            for tracks in playlist_tracks['items']:
                track_id = tracks['track']['id']
                print(tracks['track']['name'])
                track_analysis = spotify.get_track_analysis(auth_header, track_id)
                track_tempo = track_analysis['tempo']
                if(track_tempo>min_tempo and track_tempo<max_tempo):
                    print(track_analysis['tempo'])
            playlist_tracks = spotify.get_playlist_tracks(auth_header, playlist_id, offset=offset)
        #pages < 100 elements
        for tracks in playlist_tracks['items']:
            track_id = tracks['track']['id']
            name = tracks['track']['name'] 
            print(name)
            track_analysis = spotify.get_track_analysis(auth_header, track_id)
            track_tempo = track_analysis['tempo']
            if(track_tempo>min_tempo and track_tempo<max_tempo):
                print(track_analysis['tempo'])

        

        if valid_token(profile_data):
            return render_template("startFilter.html", user=profile_data)

@app.route("/filter")
def filter():
    try:
        playlist_id = request.args["playlist_id"]
        print(playlist_id)
        return make_filter(playlist_id)
    except:
        return render_template("filter.html")

def make_filter(playlist_id):
    if 'auth_header' in session:
        session['playlist_id'] = playlist_id
        auth_header = session['auth_header']
        # get profile data
        profile_data = spotify.get_users_profile(auth_header)
        # get playlist data
        playlist_data = spotify.get_playlist(auth_header, playlist_id)

        if valid_token(playlist_data):
            return render_template("filter.html", 
                                user=profile_data,
                                playlist = playlist_data)

@app.route("/callback/")
def callback():
    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return profile()

def valid_token(resp):
    return resp is not None and not 'error' in resp

# -------------------------- API REQUESTS ----------------------------

@app.route("/")
def index():
    return profile()

@app.route('/profile')
def profile():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        # get profile data
        profile_data = spotify.get_users_profile(auth_header)

        # get user playlist data
        playlist_data = spotify.get_users_playlists(auth_header)
        
        if valid_token(playlist_data):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data["items"])

    return render_template('profile.html')


if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)