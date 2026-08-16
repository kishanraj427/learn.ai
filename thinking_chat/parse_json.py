import json


def parse_json_response(answer: str):
    answer = answer.strip()

    if not answer:
        raise ValueError("Model returned an empty response.")

    try:
        data = json.loads(answer)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON:\n{answer}"
        ) from e

    if not isinstance(data, dict):
        raise ValueError("Model response must be a JSON object.")

    return data