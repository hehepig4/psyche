import re
import editdistance
from collections import defaultdict

def parse_annotation(response):
    flags = ['Analysis.Problem_Definition',
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
    # match <step step_id> step_content </step step_id>
    pattern = r'<step\s+(\d+)\s*>(.*?)</step\s+\1>'
    matches = re.findall(pattern, response, re.DOTALL)
    steps = defaultdict(list)
    
    for step_id, step_content in matches:
        step_id = int(step_id)
        answer_flags = step_content.split(';')
        
        for answer_flag in answer_flags:
            answer_flag = answer_flag.strip()
            if answer_flag in flags:
                steps[step_id].append(answer_flag)
            else:
                part = answer_flag.split('.')[-1]
                similarity = [editdistance.eval(part, flag.split('.')[-1]) for flag in flags]
                # find the closest match
                closest_flag = flags[similarity.index(min(similarity))]
                steps[step_id].append(closest_flag)
    
    return steps

def metric_full_consistency(answer_steps, grd_steps):
    step_count = 0
    c_count = 0
    for step_id, flags in grd_steps.items():
        if step_id in answer_steps:
            step_count += 1
            if set(flags) == set(answer_steps[step_id]):
                c_count += 1
    return c_count / step_count if step_count > 0 else 0