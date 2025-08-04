from basic_prompt import TASK_DESCRIPTION, PROMPT_HEADER, META_BEHAVIORS, FORMAT_DESCRIPTION, INPUT_ORGANIZATION, EXAMPLE_ORGANIZATION, TIPS
from meta_prompt import MUTATION_META_PROMPT, MERGE_META_PROMPT
import dataclasses
import copy

@dataclasses.dataclass
class Prompt:
    header: str = PROMPT_HEADER
    meta_behaviors: str = META_BEHAVIORS
    task_description: str = TASK_DESCRIPTION
    format_description: str = FORMAT_DESCRIPTION
    input_organization: str = INPUT_ORGANIZATION
    example_organization: str = EXAMPLE_ORGANIZATION
    tips: str = TIPS
    CoT: str = None
    question: str = None
    example: str = None
    groundtruth: str = None
    header_content: str = PROMPT_HEADER
    meta_behaviors_content: str = META_BEHAVIORS
    task_description_content: str = TASK_DESCRIPTION
    format_description_content: str = FORMAT_DESCRIPTION
    input_organization_content: str = INPUT_ORGANIZATION
    _rec: dict = dataclasses.field(default_factory=dict, repr=False)
    
    def __str__(self):
        return f'{self.header}\n{self.meta_behaviors}\n{self.tips}\n{self.task_description}\n{self.format_description}\n{self.input_organization}'

    def parse(self, rec):
        self.CoT = organize_cot(rec)
        self.question = rec['question']
        self.example = organize_example(rec,template=self.example_organization)
        self.input_organization_content = self.input_organization.format(problem_desc=self.question, CoT=self.CoT)
        self.groundtruth = {}
        for step_id, step in rec['steps']['reasoning'].items():
            try:
                sid = int(step_id)
            except ValueError:
                continue
            if 'human_anot' in step:
                self.groundtruth[sid] = step['human_anot']
        self._rec = rec
        
        
    def with_content(self):
        return f'{self.header_content}\n{self.meta_behaviors_content}\n{self.tips}\n{self.task_description_content}\n{self.format_description_content}\n{self.input_organization_content}'
    
    def to_dict(self):
        for field in dataclasses.fields(self):
            if field.name.endswith('_content') and not field.name.startswith('_'):
                setattr(self, field.name.replace('_content', ''), getattr(self, field.name))
        return dataclasses.asdict(self)
    
    def rebuild_example(self, annotation):
        # rebuild the example based on the annotation, groundtruth and question
        ipt_dict = {
            'question': self.question,
            'steps': {
                'reasoning': {}
            }
        }
        ori = self._rec['steps']['reasoning']
        for step_id, step in ori.items():
            try:
                sid = int(step_id)
            except ValueError:
                continue
            if sid in annotation:
                ipt_dict['steps']['reasoning'][sid] = {
                    'content': step['content'],
                    'gemini_flag': annotation[sid],
                    'human_anot': self.groundtruth.get(sid, [])
                }
            else:
                ipt_dict['steps']['reasoning'][sid] = {
                    'content': step['content']
                }
        self.example = organize_example(ipt_dict, template=self.example_organization)
        
        
    def check(self):
        errors = []
        #1. must content <step *> and </step *> in format_description
        if '<step ' not in self.format_description or '</step ' not in self.format_description:
            errors.append(ValueError("Format description must contain <step *> and </step *> tags."))
        #2. must content <explanation *> and </explanation *> in format_description
        #deprecated
        # if '<explanation ' not in self.format_description or '</explanation ' not in self.format_description:
        #     errors.append(ValueError("Format description must contain <explanation *> and </explanation *> tags."))
        #3. {problem_desc} and {CoT} must be in input_organization
        if '{problem_desc}' not in self.input_organization or '{CoT}' not in self.input_organization:
            errors.append(ValueError("Input organization must contain {problem_desc} and {CoT} placeholders."))
        #4. meta_behaviors must retain the same name and exist in the flags
        flags = [
            "Analysis.Problem_Definition",
            "Analysis.Information_Organization",
            "Analysis.Problem_Structuring",
            "Inference.Deductive_Reasoning",
            "Inference.Inductive_Reasoning",
            "Inference.Abductive_Reasoning",
            "Judgment.Principle_Selection",
            "Judgment.Evaluation_of_Alternatives",
            "Judgment.Conclusion_Decision",
            "Suggestion.Strategic_Planning",
            "Suggestion.Branch_Changing",
            "Suggestion.Hypothesis_Generation",
            "Suggestion.Analogy_Recall",
            "Reflection.Self_Monitoring_Evaluation",
            "Reflection.Counterfactual_Thinking",
            "Reflection.Causal_Attribution",
            "Reflection.Strategy_Regulation"
        ]
        for flag in flags:
            if flag not in self.meta_behaviors_content:
                errors.append(ValueError(f"Meta-behavior '{flag}' must be present in the meta-behaviors content."))
        return errors if errors else None
    
    @staticmethod
    def mutation_meta_prompt(prompt, part_name='part'):
        # part_names = ['prompt_header', 'prompt_meta_behaviors', 'prompt_task_description', 'prompt_format_description', 'prompt_input_organization']
        return MUTATION_META_PROMPT.format(
            prompt_header=prompt.header,
            prompt_meta_behaviors=prompt.meta_behaviors,
            prompt_tips=prompt.tips,
            prompt_task_description=prompt.task_description,
            prompt_format_description=prompt.format_description,
            prompt_input_organization=prompt.input_organization,
            example=prompt.example,
            part_name=part_name
        )
        
    @staticmethod
    def merge_meta_prompt(prompt_1, prompt_2):
        return MERGE_META_PROMPT.format(
            prompt_header_1=prompt_1.header,
            prompt_meta_behaviors_1=prompt_1.meta_behaviors,
            prompt_tips_1=prompt_1.tips,
            prompt_task_description_1=prompt_1.task_description,
            prompt_format_description_1=prompt_1.format_description,
            prompt_input_organization_1=prompt_1.input_organization,
            prompt_header_2=prompt_2.header,
            prompt_meta_behaviors_2=prompt_2.meta_behaviors,
            prompt_tips_2=prompt_2.tips,
            prompt_task_description_2=prompt_2.task_description,
            prompt_format_description_2=prompt_2.format_description,
            prompt_input_organization_2=prompt_2.input_organization
        )
    
    @staticmethod
    def parse_mutated(ori_prompt, response, part_name='prompt_meta_behaviors'):
        """
        Parse the mutated part from the response and update the corresponding part in the prompt.
        """
        import re
        pattern = r'<mutated_part>\s*(.*?)\s*</mutated_part>'
        match = re.findall(pattern, response, re.DOTALL)
        if not match:
            raise ValueError("Response does not contain a valid mutated part.")
        match = match[-1]
        new_prompt = copy.deepcopy(ori_prompt)
        setattr(new_prompt, part_name.replace('prompt_', ''), match.strip())
        return new_prompt

    @staticmethod
    def parse_merged(ori_prompt, response):
        """
        Parse the merged prompt from the response and return a new Prompt object.
        """
        import re
        pattern = r'<prompt_header>\s*(.*?)\s*</prompt_header>\s*<prompt_meta_behaviors>\s*(.*?)\s*</prompt_meta_behaviors>\s*<prompt_tips>\s*(.*?)\s*</prompt_tips>\s*<prompt_task_description>\s*(.*?)\s*</prompt_task_description>\s*<prompt_format_description>\s*(.*?)\s*</prompt_format_description>\s*<prompt_input_organization>\s*(.*?)\s*</prompt_input_organization>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            new_prompt = copy.deepcopy(ori_prompt)
            new_prompt.header = match.group(1).strip()
            new_prompt.meta_behaviors = match.group(2).strip()
            new_prompt.tips = match.group(3).strip()
            new_prompt.task_description = match.group(4).strip()
            new_prompt.format_description = match.group(5).strip()
            new_prompt.input_organization = match.group(6).strip()
            return new_prompt
        else:
            raise ValueError("Response does not contain a valid merged prompt.")


def organize_cot(rec, content_key='content'):
    cot = {}
    for step_id, step in rec['steps']['reasoning'].items():
        try:
            sid = int(step_id)
        except ValueError:
            continue
        if content_key in step:
            temp = f'<step {sid}> {step[content_key]} </step {sid}>'
            cot[sid] = temp
    cot = sorted(cot.items(), key=lambda x: x[0])
    return '\n'.join([item[1] for item in cot])

def organize_example(example_rec, response_key='gemini_flag', answer_key='human_anot', content_key='content', response_tag='attempt', 
                     answer_tag='answer',template=EXAMPLE_ORGANIZATION):
    # question at example_rec['question']
    # steps at example_rec['steps']['reasoning'][step_id][key] : -> list of flags, ';'.join(steps)
    question = example_rec['question']
    contents = example_rec['steps']['reasoning']
    cot = {}
    reasoning = {}
    for step_id, step in contents.items():
        temp = ''
        try:
            sid = int(step_id)
        except ValueError:
            continue
        if response_key in step:
            response = step[response_key]
            if isinstance(response, list):
                response = ';'.join(response)
            temp += f'<{response_tag} {sid}> {response} </{response_tag} {sid}> '
        if answer_key in step:
            answer = step[answer_key]
            if isinstance(answer, list):
                answer = ';'.join(answer)
            temp += f'<{answer_tag} {sid}> {answer} </{answer_tag} {sid}> '
        reasoning[sid] = temp
        cot[sid] = f'<step {sid}> {step[content_key]} </step {sid}>'
    
    cot = sorted(cot.items(), key=lambda x: x[0])
    reasoning = sorted(reasoning.items(), key=lambda x: x[0])
    cot = [item[1] for item in cot]
    reasoning = [item[1] for item in reasoning]    
    
    return template.format(question=question, reasoning='\n'.join(cot), example='\n'.join(reasoning))

if __name__ == '__main__':
    import json
    import os
    
    example_file = './all/reanot/R1/254_R1_AIME_1_10.json'
    target_file = './all/human_original/R1/501_R1_AIME_1_11.json'
    
    with open(example_file, 'r') as f:
        example_rec = json.load(f)
    with open(target_file, 'r') as f:
        target_rec = json.load(f)
    target_prompt = Prompt()
    target_prompt.parse(target_rec, example_rec=example_rec)
    #print(target_prompt.with_content())
    #print(target_prompt.check())
    #print(Prompt.mutation_meta_prompt(target_prompt, part_name='prompt_meta_behaviors'))
    print(Prompt.merge_meta_prompt(target_prompt, target_prompt))