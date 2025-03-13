import re


def parse_event_data(content):
    decode_content = content.decode("utf-8")
    decode_content = decode_content.split("\r\n")
    decode_content.pop()
    def deep_set(dic, keys, value):
        for i, key in enumerate(keys[:-1]):
            if isinstance(key, int):
                while isinstance(dic, dict) and key not in dic:
                    dic[key] = []
                if isinstance(dic, list):
                    while len(dic) <= key:
                        dic.append({})
                dic = dic[key]
            else:
                if key not in dic:
                    next_key = keys[i + 1]
                    dic[key] = [] if isinstance(next_key, int) else {}
                dic = dic[key]

        if isinstance(keys[-1], int):
            if not isinstance(dic, list):
                dic[keys[-1]] = []
            while len(dic) <= keys[-1]:
                dic.append(None)
            dic[keys[-1]] = value
        else:
            dic[keys[-1]] = value

    def parse_key(key):
        parts = re.split(r"\.|\[|\]", key)
        keys = [int(part) if part.isdigit() else part for part in parts if part]
        return keys

    def decode_to_json(decode_content: list):
        result = {}
        for content in decode_content:
            key, value = content.split("=")
            keys = parse_key(key)
            deep_set(result, keys, value)
        result = result.get("Events", [{}])[0]
        return result

    return decode_to_json(decode_content)

def parse_text_data(text):
    decode_content = text.split("\r\n")
    decode_content.pop()
    def deep_set(dic, keys, value):
        for i, key in enumerate(keys[:-1]):
            if isinstance(key, int):
                while isinstance(dic, dict) and key not in dic:
                    dic[key] = []
                if isinstance(dic, list):
                    while len(dic) <= key:
                        dic.append({})
                dic = dic[key]
            else:
                if key not in dic:
                    next_key = keys[i + 1]
                    dic[key] = [] if isinstance(next_key, int) else {}
                dic = dic[key]

        if isinstance(keys[-1], int):
            if not isinstance(dic, list):
                dic[keys[-1]] = []
            while len(dic) <= keys[-1]:
                dic.append(None)
            dic[keys[-1]] = value
        else:
            dic[keys[-1]] = value

    def parse_key(key):
        parts = re.split(r"\.|\[|\]", key)
        keys = [int(part) if part.isdigit() else part for part in parts if part]
        return keys

    def decode_to_json(decode_content: list):
        result = {}
        for content in decode_content:
            key, value = content.split("=")
            keys = parse_key(key)
            deep_set(result, keys, value)
        return result

    return decode_to_json(decode_content)