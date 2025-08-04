import os
import json
import copy
import editdistance
merge_paths = [
    './output/AIME'
]

model_names = [
    'gemini-best',
]

opt_dir = './machine_annotations/AIME' #for example

all_steps_r1 = 0
all_steps_qwq = 0
files = os.listdir(merge_paths[0])
for file in files:
    target_rec = {}
    for model_name in model_names:
        target_rec[model_name+'_flag'] = ['Analysis.Problem_Definition',
                                            'Analysis.Information_Organization',
                                            'Analysis.Problem_Structuring',
                                            'Inference.Deductive_Reasoning',
                                            'Inference.Inductive_Reasoning',
                                            'Inference.Abductive_Reasoning',
                                            'Judgment.Principle_Selection',
                                            'Judgment.Evaluation_of_Alternatives',
                                            'Judgment.Conclusion_Decision',
                                            'Suggestion.Strategic_Planning',
                                            'Suggestion.Branch_Changing',
                                            'Suggestion.Hypothesis_Generation',
                                            'Suggestion.Analogy_Recall',
                                            'Reflection.Self_Monitoring_Evaluation',
                                            'Reflection.Counterfactual_Thinking',
                                            'Reflection.Causal_Attribution',
                                            'Reflection.Strategy_Regulation'
                                            ]
    target_rec['human_anot'] = ['Analysis.Problem_Definition',
                                            'Analysis.Information_Organization',
                                            'Analysis.Problem_Structuring',
                                            'Inference.Deductive_Reasoning',
                                            'Inference.Inductive_Reasoning',
                                            'Inference.Abductive_Reasoning',
                                            'Judgment.Principle_Selection',
                                            'Judgment.Evaluation_of_Alternatives',
                                            'Judgment.Conclusion_Decision',
                                            'Suggestion.Strategic_Planning',
                                            'Suggestion.Branch_Changing',
                                            'Suggestion.Hypothesis_Generation',
                                            'Suggestion.Analogy_Recall',
                                            'Reflection.Self_Monitoring_Evaluation',
                                            'Reflection.Counterfactual_Thinking',
                                            'Reflection.Causal_Attribution',
                                            'Reflection.Strategy_Regulation'
                                            ]
    if file.endswith('.json'):
        recs = []
        for path in merge_paths:
            with open(os.path.join(path, file), 'r') as f:
                data = json.load(f)
                recs.append(data)
        if not recs:
            continue
        format_keys = ['reasoning', 'answer']
        target_rec.update(recs[0])  # Use the first record as a base
        target_rec['question'] = recs[0]['question']
        target_rec['steps'] = {}
        if 'Math' or 'MATH' in merge_paths[0]:
            target_rec['True_Answer'] = recs[0]['final_answer']
        elif 'Common' in merge_paths[0]:
            target_rec['True_Answer'] = recs[0]['answerKey']
        steps_cnt = 0
        for key in format_keys:
            temp = {}
            for i ,(name, rec) in enumerate(zip(model_names, recs)):
                for struc in rec['structure']:
                    if struc['format'] == key:
                        for j, res in enumerate(struc['results']):
                            if res['step'] not in temp:
                                temp[res['step']] = {}
                                temp[res['step']]['content']= res['content']
                            #temp[res['step']][name + '_flag'] = res['flag'].replace(" ","").split(';')
                            _flag = res['flag'].replace(" ","").split(';')
                            flags = target_rec[name + '_flag']
                            if _flag !=['']:
                                fix_flag = []
                                for f in _flag:
                                    if f in flags:
                                        fix_flag.append(f)
                                    else:
                                        #try to fuzzy match
                                        if '.' in f:
                                            parts = f.split('.')[-1]
                                        elif '.' in _flag:
                                            parts = _flag.split('.')[-1]
                                        else:
                                            parts = f
                                        distances = [(i, editdistance.eval(parts, grd)) for i, grd in enumerate(flags)]
                                        min_distance = min(distances, key=lambda x: x[1])
                                        fix_flag.append(flags[min_distance[0]])
                                temp[res['step']][name + '_flag'] = fix_flag
                            else:
                                temp[res['step']][name + '_flag'] = []


                            temp[res['step']][name + '_explanation'] = res['explanation']
                        temp[name + '_response'] = struc['response']
                        
            
            
            flags = [model_name+'_flag' for model_name in model_names]
            for step in temp:
                if not isinstance(temp[step], dict):
                    continue
                steps_cnt += 1
                # check if all model names have the same flag
                consistency = True
                sorted_flags = [
                    sorted(temp[step][flag]) for flag in flags if flag in copy.deepcopy(temp[step])
                ]
                if len(sorted_flags) == 1 or len(set([''.join(_) for _ in sorted_flags])) != 1:
                    # all models agree on the flag
                    consistency = False

            target_rec['steps'][key] = temp
        # Save the modified data back to a new JSON file
        
        if 'R1' in file:
            os.makedirs(os.path.join(opt_dir, 'R1'), exist_ok=True)
            with open(os.path.join(opt_dir, 'R1',str(steps_cnt)+'_'+file), 'w') as f:
                json.dump(target_rec, f, indent=4)
            pass
            all_steps_r1 += steps_cnt
        else:
            os.makedirs(os.path.join(opt_dir, 'QwQ'), exist_ok=True)
            with open(os.path.join(opt_dir, 'QwQ',str(steps_cnt)+'_'+file), 'w') as f:
                json.dump(target_rec, f, indent=4)
            pass
            all_steps_qwq += steps_cnt
            
print('all steps in R1:', all_steps_r1)
print('all steps in QwQ:', all_steps_qwq)