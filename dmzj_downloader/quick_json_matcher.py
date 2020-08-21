__all__ = (
    'match_first_json',
)

from typing import Dict, Any, Union, List
from itertools import islice
import json

MATCH_BRACKET = {
    '[': ']',
    '{': '}',
}


def match_first_json(text: str) -> Union[Dict[str, Any], list]:
    if text[0] in MATCH_BRACKET:
        left_bracket, right_bracket = text[0], MATCH_BRACKET[text[0]]
    else:
        raise ValueError('文本的第一个字符必须为左括号。')

    count = 0
    state = 0
    last_char_index = -1
    for i, c in enumerate(text):
        if state == 0:
            if c == left_bracket:
                count += 1
            elif c == right_bracket:
                count -= 1
                if count == 0:
                    last_char_index = i
                    break

            elif c == '"':
                state = 1

        elif state == 1:
            if c == '"':
                state = 0
            elif c == '\\':
                state = 2
        elif state == 2:
            state = 1

    if last_char_index < 0:
        raise ValueError('尝试匹配出完整的 JSON 失败。')

    json_text = text[:last_char_index + 1]
    return json.loads(json_text)
