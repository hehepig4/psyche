from openai import OpenAI
import pickle as pkl
import os
#import logging
# API configuration - set these environment variables before running
API_KEY = ''
BASE_URL = ''
def create_client():
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL,timeout=1800)
    return client


def generate_ans(client, content, model="google/gemini-2.5-flash-preview-05-20"):
    # log called
    # print(" - [log] Generating answer with LLM for content: {}...".format(content[:50].replace('\n',' ')))  # Log the first 50 characters of content
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": content},
            #{"role": "assistant","content" : format['assistant_content'],"prefix": True}
        ],
        max_tokens=60000,
        temperature=0.4,
        seed=42
    )
    #sleep(3)
    # 
    input_tokens = response.usage.prompt_tokens
    print(f" - [log] Input tokens: {input_tokens}")  # Log the input tokens
    return  response.choices[0].message.content

class MutationCache:
    def __init__(self, file_path=None,load_existing=False):
        self.file_path = file_path
        if load_existing and file_path is not None and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self.cache = pkl.load(f)
        else:
            if file_path is not None:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            else:
                raise ValueError("File path must be specified to load or save the cache.")
            self.cache = []
        
    def add(self, ori_prompt, mutation_args, mutated_prompt, ori_response):
        self.cache.append({
            'ori_prompt': ori_prompt,
            'mutation_args': mutation_args,
            'mutated_prompt': mutated_prompt,
            'ori_response': ori_response
        })
        
    def save(self, file_path=None):
        _fp = self.file_path if file_path is None else file_path
        if _fp is None:
            raise ValueError("File path must be specified to save the cache.")
        
        os.makedirs(os.path.dirname(_fp), exist_ok=True)
        
        with open(_fp, 'wb') as f:
            pkl.dump(self.cache, f)
