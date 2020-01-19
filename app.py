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