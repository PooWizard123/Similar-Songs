from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import render_template
from numpy import dot
from numpy.linalg import norm

song_data = pd.read_csv('spotify_songs.csv', encoding='latin1')

cols = ['track_album_id', 'track_popularity', 'track_album_name', 'track_album_release_date', 'playlist_id', 'duration_ms']
song_data.drop(cols, axis=1, inplace = True)
song_data.dropna(inplace=True)

X = song_data
X['track_artist_factori'] = X['track_artist'].factorize()[0]
X['playlist_name'] = X['playlist_name'].factorize()[0]
X['playlist_genre'] = X['playlist_genre'].factorize()[0]
X['playlist_subgenre'] = X['playlist_subgenre'].factorize()[0]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
app.app_context().push()

@app.route("/")
@app.route("/index", methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/search")
def search():
    q = request.args.get('q')
    if q:
        results = Music.query.filter(Music.title.icontains(q) | Music.artist.icontains(q)).limit(100).all()
    else:
        results = []
    return render_template('search_results.html', results = results)

@app.route("/findsim", methods = ['GET', 'POST'])
def findsim():
    most_similar = {}
    if request.method == 'POST':
        id = list(request.form.keys())[0]
        curr_song = X.loc[X['track_id'] == id].iloc[0]

        for i in range(len(X)):
            if X.iloc[i]['playlist_name'] == curr_song['playlist_name']:
                song_name = X.iloc[i]['track_name']
                a = curr_song.drop(['track_name', 'track_artist', 'track_id'])
                b = X.iloc[i].drop(['track_name', 'track_artist', 'track_id'])
                cos_sim = dot(a,b)/(norm(a)*norm(b))
                most_similar[song_name] = cos_sim
        sorted_songs = sorted(most_similar.items(), key=lambda x:x[1], reverse = True)
        sorted_songs = sorted_songs[1:6]
        
        s_and_id = {}
        for song, cossim in sorted_songs:
            found = X.loc[X['track_name'] == song].iloc[0]
            s_and_id[song] = found['track_id']
        print(s_and_id)

    return render_template('find.html', most_similar = s_and_id, s_name = curr_song['track_name'])


class Music(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    song_id = db.Column(db.String(300), nullable = False)
    title = db.Column(db.String(300), nullable = False)
    artist = db.Column(db.String(300), nullable = False)
    
if __name__ == '__main__':
    app.run()

