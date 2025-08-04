#parse CoT to format

def parse_cot(cot):
    #steps sep by \n\n
    steps = cot.split('\n\n')
    opt = '\n'
    struc = []
    for i, step in enumerate(steps):
        #find step number
        opt += f'<step {i+1}>\n'+step+f'\n</step {i+1}>\n'
        struc.append(
            {
                'step': i+1,
                'content': step
            }
        )
    return opt, struc


def parse_anot_v1(rec, format_key='reasoning'):
    question = rec['question']
    response = rec[format_key]
    cot = response.split('</think>')[0]
    return question, cot

