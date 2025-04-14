### blueprints/challenge_api.py  
from flask import Blueprint, request, jsonify
from models.room_model import Room
from models.word_model import Word
from models.wordchallenge_models import WordChallenge
from redis_utils import set_room_state
import random

challenge_api = Blueprint("challenge_api", __name__)

@challenge_api.route('/api/challenge/create', methods=['POST'])
def create_challenge():
    data = request.json
    room_id = data.get('room_id')
    owner_id = int(data.get('owner_id'))
    num_words = data.get('num_words', 5)

    room = Room.get_room_by_id(room_id)
    if not room or room['owner_id'] != owner_id:
        return jsonify({"error": "无权限创建挑战"}), 403

    all_words = Word.get_all_words()
    if len(all_words) < num_words:
        return jsonify({"error": "单词库不足"}), 400

    selected = random.sample(all_words, num_words)
    word_ids = [word['id'] for word in selected]

    challenge_ids = []
    for i, word_id in enumerate(word_ids):
        challenge_id = WordChallenge.create_challenge(room_id, word_id, round_number=i + 1)
        challenge_ids.append(challenge_id)

    set_room_state(room_id, {
        "challenge_ids": challenge_ids,
        "current_index": 0
    })

    return jsonify({"challenge_id": challenge_ids[0]})