### redis_utils.py
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def set_room_state(room_id, state: dict):
    r.set(f"room_state:{room_id}", json.dumps(state))

def get_room_state(room_id):
    val = r.get(f"room_state:{room_id}")
    return json.loads(val) if val else None

def del_room_state(room_id):
    r.delete(f"room_state:{room_id}")
