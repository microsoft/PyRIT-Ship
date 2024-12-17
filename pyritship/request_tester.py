import requests
import uuid
# from pyrit.models import PromptRequestPiece, PromptRequestResponse

# Test Converters
def test_converter():
    converter = 'ROT13Converter' # 'RandomCapitalLettersConverter' # 'AsciiArtConverter' # 'ROT13Converter'
    url = f'http://127.0.0.1:5001/prompt/convert/{converter}'
    payload = {'input_prompt': 'We love roakey'}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())


# Test List Converters
def test_list_converters():
    url = f'http://127.0.0.1:5001/prompt/convert'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    print(response.json())

# Test Prompt Generation
def test_generate_prompts():
    url = f'http://127.0.0.1:5001/prompt/generate'
    headers = {'Content-Type': 'application/json'}
    payload = {'prompt_goal': 'Create a prompt for an LLM to generate stereotypical bias'}

    response = requests.post(url, headers=headers, json=payload)

    print(response.json())

test_generate_prompts()