from parse import parse_cot,parse_anot_v1
import os
import json
from classify.utils import create_client,  generate_ans_v3
import re



def for_anot_v1(folder='math',out_dir='output/parse/math',model="deepseek-v3-250324",max_numbers=-1):
    client = create_client()
    fmkeys = ['reasoning']
    if max_numbers == -1:
        max_numbers = int(1e10)
    for _c, file in enumerate(os.listdir(folder)):
        if _c >= max_numbers:
            break
        try:
            if os.path.exists(os.path.join(out_dir,file)):
                continue  # Skip files that already exist in the output directory
            with open(os.path.join(folder,file),'r') as f:
                rec = json.load(f)
                
            if os.path.exists(os.path.join(out_dir,file)):
                _rec = json.load(open(os.path.join(out_dir,file),'r'))
                for struc in _rec['structure']:
                    if struc['format'] in fmkeys:
                        fmkeys.remove(struc['format'])

            for format_key in fmkeys:
                if format_key not in rec.keys():
                    continue
                question, cot= parse_anot_v1(rec,format_key=format_key)
                cot, struc = parse_cot(cot)
                response = generate_ans_v3(client,question,cot,model)
                
                #try to find all closed targets <step i>, <explanation i>  and assign to struc
                for i in range(len(struc)):
                    flag = re.search('<step {}>(.*?)</step {}>'.format(i+1, i+1), response, re.DOTALL)
                    step_flag = flag.group(1) if flag else ''
                    explanation = re.search('<explanation {}>(.*?)</explanation {}'.format(i+1,i+1),response, re.DOTALL)
                    expl_flag = explanation.group(1) if explanation else ''
                    struc[i]['flag'] = step_flag
                    struc[i]['explanation'] = expl_flag

                    
                # with open(os.path.join(out_dir,file),'w') as f:
                #     json.dump(response,f)
                if 'structure' in rec.keys():
                    rec['structure'].extend([{'results': struc,
                                            'model': model,
                                            'response':response,
                                            'format': format_key}])
                else:
                    rec.update({'structure':[{'results': struc,
                                            'model': model,
                                            'response':response,
                                            'format': format_key}]
                                }) 
                if os.path.exists(os.path.join(out_dir,file)):
                    _rec = json.load(open(os.path.join(out_dir,file),'r'))
                    if 'structure' in _rec:
                        rec['structure'].extend(_rec['structure'])
                
            with open(os.path.join(out_dir,file),'w') as f:
                json.dump(rec,f, indent=4)
            print(f"Done {file}")
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

        
if __name__ == '__main__':

    for_anot_v1(folder='./data/AIME',out_dir='./output/AIME', model='google/gemini-2.5-flash-preview-05-20') # for an example
