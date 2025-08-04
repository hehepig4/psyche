
from time import sleep
from config import API_KEY, BASE_URL, PROMPT
from openai import OpenAI




def create_client():
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=1800)
    return client


def generate_ans_v3(client, problem, cot, model="deepseek-v3-241226"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": PROMPT.format(problem_desc=problem, CoT=cot)},
            #{"role": "assistant","content" : format['assistant_content'],"prefix": True}
        ],
        max_tokens=46000,
        temperature=0.6,
    )
    #sleep(3)
    return  response.choices[0].message.content


