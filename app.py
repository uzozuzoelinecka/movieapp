from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import requests
import qrcode
import io
from base64 import b64encode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app)

# TMDB API configuration
tmdb_api_key = 'your_tmdb_api_key'

@app.route('/movie-picker', methods=['GET'])
def movie_picker():
    mode = request.args.get('mode', 'single')  # single or group
    if mode == 'single':
        return jsonify(pick_random_movie()), 200
    else:
        return jsonify(pick_random_movies()), 200

def pick_random_movie():
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    return data['results'][0] if data['results'] else {}  # Return the first popular movie

def pick_random_movies(count=3):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=en-US&page=1'
    response = requests.get(url)
    data = response.json()
    return data['results'][:count] if data['results'] else []  # Return multiple popular movies

@app.route('/generate-qrcode/<string:content>', methods=['GET'])
def generate_qr_code(content):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return jsonify({'qrcode': b64encode(img_byte_arr.getvalue()).decode('utf-8')}), 200

@socketio.on('request_movie')
def handle_request_movie(data):
    movie = pick_random_movie()
    emit('response_movie', movie)

if __name__ == '__main__':
    socketio.run(app, debug=True)