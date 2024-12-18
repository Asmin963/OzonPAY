import json
import os

PATH = os.path.join(os.path.dirname(__file__), "..", "files", "states.json")

def _create_dirs():
    if not os.path.exists("../files"):
        os.makedirs("../files")


def save_states(states: dict, path=PATH) -> dict:
    with open(path, "w", encoding='utf-8') as f:
        json.dump(states, f, indent=4, ensure_ascii=False)
        return states


def load_states(path=PATH) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
            return {float(k): v for k, v in data.items()}
    else:
        return {}
