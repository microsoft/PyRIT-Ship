# app.py
from flask import Flask, request, jsonify
import asyncio
import os
import inspect
import importlib
from pyrit.common import default_values
from pyrit.setup import initialize_pyrit_async, IN_MEMORY
from pyrit.prompt_converter import PromptConverter
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.executor.attack import PromptSendingAttack, MarkdownAttackResultPrinter
from pyrit.score import SelfAskTrueFalseScorer
from dotenv import load_dotenv

app = Flask(__name__)
chat_target = None

@app.route('/prompt/convert')
def list_converters():
    converters = PromptConverter.__subclasses__()
    converter_list = []
    for converter in converters:
        print( converter.__name__)
        params = inspect.signature(converter.__init__).parameters
        if ((len(params) == 1 and "self" in params) or (len(params) == 3 and "self" in params and "kwargs" in params and "args" in params)):
            converter_list.append(converter.__name__)
        else:
            defaults = [p for p in params if params[p].default != inspect.Parameter.empty]
            print("    params", len(params), "; defaults: ", len(defaults))
            if (len(defaults) == len(params) - 1): # all defaults but self
                converter_list.append(converter.__name__)
    return jsonify(converter_list)

@app.route('/prompt/convert/<converter_name>', methods=['POST'])
def convert(converter_name:str):
    # Extract input data from json payload
    data = request.get_json()
    input_prompt = data['text']

    # Process input data with PyRIT converters
    c = next((cls for cls in PromptConverter.__subclasses__() if cls.__name__ == converter_name), None)
    try:
        module = importlib.import_module(c.__module__)
        converter_class = getattr(module, c.__name__)
        instance = converter_class()

        converted_prompt = asyncio.run(instance.convert_async(prompt=input_prompt, input_type="text"))
        return jsonify({"converted_text": converted_prompt.output_text})
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/prompt/generate', methods=['POST'])
def generate_prompt():
    # Initialize chat target
    global chat_target
    if (chat_target is None):
        chat_target = initialize_chat_target()
    
    prompt_sending_attack = PromptSendingAttack(objective_target=chat_target)
    # Extract input data from json payload
    data = request.get_json()
    prompt_goal = data['prompt_goal']

    result = asyncio.run(prompt_sending_attack.execute_async(objective=prompt_goal)).last_response.converted_value

    return jsonify({"prompt": result})

@app.route('/prompt/score/SelfAskTrueFalseScorer', methods=['POST'])
def score():
    # Initialize chat target
    global chat_target
    if (chat_target is None):
        chat_target = initialize_chat_target()

    # Extract input data from json payload
    score_json = request.get_json()
    true_description = score_json["scoring_true"]
    false_description = score_json["scoring_false"]
    prompt_response_to_score = score_json["prompt_response"]

    scorer = SelfAskTrueFalseScorer(
        chat_target = chat_target,
        true_false_question={ 
            "category": "pyritship", 
            "true_description": true_description, 
            "false_description": false_description
            }
    )

    scored_response = asyncio.run(scorer.score_text_async(text=prompt_response_to_score))[0]
    return jsonify(
         {
            "scoring_text": str(scored_response.get_value()),
            "scoring_metadata": scored_response.score_metadata,
            "scoring_rationale": scored_response.score_rationale
         }
    )
    
def initialize_chat_target():
    asyncio.run(initialize_pyrit_async(memory_db_type=IN_MEMORY))

    chat_target = OpenAIChatTarget(
        model_name=os.environ.get("OPENAI_CHAT_MODEL_NAME"),
        endpoint=os.environ.get("OPENAI_CHAT_ENDPOINT"),
        api_key=os.environ.get("OPENAI_CHAT_KEY")
    )
    return chat_target

if __name__ == '__main__':
    if os.environ.get("OPENAI_CHAT_ENDPOINT") is None:
        load_dotenv()
    app.run(host='127.0.0.1', port=5001, debug=True, threaded=False)
