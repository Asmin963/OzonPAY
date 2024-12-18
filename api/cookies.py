import json
import os

PATH = os.path.join(os.path.dirname(__file__), "..", "files", "cookies.json")

def save_cookies(cookies: str | dict, path=PATH) -> dict:
    with open(path, "w", encoding='utf-8') as f:
        if isinstance(cookies, str):
            cookies = {k: v for k, v in [c.split("=") for c in cookies]}
        json.dump(cookies, f, indent=4, ensure_ascii=False)
        return cookies


def load_cookies(path=PATH, return_str: bool = True) -> dict | str:
    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            res = json.load(f)
            if return_str:
                res = "; ".join([f"{k}={v}" for k, v in res.items()])
            return res
    else:
        return "" if return_str else {}