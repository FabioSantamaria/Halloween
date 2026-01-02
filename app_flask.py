import os
import json
import random
import yaml
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Constants
WORDS_FILE = 'halloween_words.yml'
SCORES_FILE = 'scores.json'

def load_words():
    try:
        with open(WORDS_FILE, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {"pictionary": [], "mimic": []}

def load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/words/<mode>', methods=['GET'])
def get_word(mode):
    words_data = load_words()
    words_list = words_data.get(mode, [])
    if not words_list:
        return jsonify({"error": "No words found for this mode"}), 404
    word = random.choice(words_list)
    return jsonify({"word": word})

@app.route('/api/scores', methods=['GET', 'POST'])
def handle_scores():
    if request.method == 'GET':
        return jsonify(load_scores())
    elif request.method == 'POST':
        scores = request.json
        save_scores(scores)
        return jsonify({"success": True, "scores": scores})

@app.route('/api/teams', methods=['POST', 'DELETE'])
def handle_teams():
    scores = load_scores()
    data = request.json
    team_name = data.get('team')
    
    if not team_name:
        return jsonify({"error": "Team name required"}), 400

    if request.method == 'POST':
        if team_name not in scores:
            scores[team_name] = 0
            save_scores(scores)
            return jsonify({"success": True, "message": "Team added", "scores": scores})
        else:
            return jsonify({"error": "Team already exists"}), 409
            
    elif request.method == 'DELETE':
        if team_name in scores:
            del scores[team_name]
            save_scores(scores)
            return jsonify({"success": True, "message": "Team removed", "scores": scores})
        else:
            return jsonify({"error": "Team not found"}), 404

@app.route('/api/reset', methods=['POST'])
def reset_scores():
    scores = load_scores()
    for team in scores:
        scores[team] = 0
    save_scores(scores)
    return jsonify({"success": True, "scores": scores})

if __name__ == '__main__':
    # Use PORT environment variable for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
