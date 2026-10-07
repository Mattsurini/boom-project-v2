import json
from flask import Flask, jsonify, request
import os

DATA_PATH = 'E:/Boom Project/Output/Sources/Chinese-Astrology/chinese_calendar_oct2026.json'

app = Flask(__name__)

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    DATA = json.load(f)

INDEX = {item['date']: item for item in DATA}

@app.route('/almanac/<date_str>')
def almanac(date_str):
    item = INDEX.get(date_str)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(item)

@app.route('/almanac')
def almanac_query():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'date required'}), 400
    return almanac(date_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
