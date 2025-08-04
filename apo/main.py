from utils import create_client, generate_ans, MutationCache
from evaluate_prompt import parse_annotation, metric_full_consistency
from organize import Prompt
import json
import copy
import os
import random
import numpy as np
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import pickle as pkl
from collections import defaultdict
#thread pool in a subprocess


class Population:
    def __init__(self,):
        self.prompts = []
        self.consistencies = []
    
    def add(self, prompt, consistency):
        self.prompts.append(prompt)
        self.consistencies.append(consistency)
    
    def __len__(self):
        return len(self.prompts)
    
    def __getitem__(self, idx):
        if idx < 0 or idx >= len(self.prompts):
            raise IndexError("Index out of range")
        return self.prompts[idx], self.consistencies[idx]
    
    def topk(self, k):
        if k > len(self.prompts):
            raise ValueError("k cannot be greater than the number of prompts in the population")
        sorted_indices = sorted(range(len(self.consistencies)), key=lambda i: self.consistencies[i], reverse=True)
        top_prompts = [self.prompts[i] for i in sorted_indices[:k]]
        top_consistencies = [self.consistencies[i] for i in sorted_indices[:k]]
        return top_prompts, top_consistencies

    def save(self, file_path):
        """
        Save the population to a file.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # pickle the prompts and consistencies
        with open(file_path, 'wb') as f:
            pkl.dump({
                'prompts': self.prompts,
                'consistencies': self.consistencies
            }, f)

    def load(self, file_path):
        """
        Load the population from a file.
        """
        with open(file_path, 'rb') as f:
            data = pkl.load(f)
            self.prompts = data['prompts']
            self.consistencies = data['consistencies']

    def kill(self, alive):
        """
        Remove the worst and identical prompts until the population size is equal to alive.
        """
        if alive >= len(self.prompts):
            return
        # remove identical prompts first, measure by the consistency
        unique_prompts = defaultdict(list)
        for i in range(len(self.prompts)):
            unique_prompts[round(self.consistencies[i], 3)].append(i)
        # keep only one prompt for each unique consistency
        to_remove = []
        for indices in unique_prompts.values():
            if len(indices) > 1:
                # keep the first one, remove the rest
                random.shuffle(indices)
                to_remove.extend(indices[1:])
        to_remove = sorted(set(to_remove), reverse=True)
        for idx in to_remove:
            self.prompts.pop(idx)
            self.consistencies.pop(idx)
        if alive >= len(self.prompts):
            return
        assert all(self.consistencies[i] >= 0 for i in range(len(self.consistencies))), "All consistencies must be non-negative"
        sorted_indices = sorted(range(len(self.consistencies)), key=lambda i: self.consistencies[i])
        indices_to_remove = sorted_indices[:len(self.prompts) - alive]
        for idx in sorted(indices_to_remove, reverse=True):
            self.prompts.pop(idx)
            self.consistencies.pop(idx)

def try_with_budget(func, *args, **kwargs):
    """
    Try to execute a function with a budget of attempts.
    If the function fails, it will retry up to the budget limit.
    """
    budget = 3
    for attempt in range(budget):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{budget} failed: {e}")
            if attempt == budget - 1:
                return None
            continue

def _safe_wrapper_with_budget(func_and_args):
    """Safe wrapper for parallel execution with retry mechanism"""
    func, args = func_and_args
    budget = 1
    for attempt in range(budget):
        try:
            return func(args)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{budget} failed: {e}")
            if attempt == budget - 1:
                return None
            continue

def parallel_try_with_budget(func, args_list, kwargs_list=None, max_workers=16):
    """
    Try to execute a function with a budget of attempts in parallel.
    If the function fails, it will retry up to the budget limit.
    """
    if kwargs_list is None:
        kwargs_list = [{}] * len(args_list)
    
    func_and_args_list = [(func, args) for args in args_list]

    with Pool(processes=min(max_workers,len(func_and_args_list))) as pool:
        results = pool.map(_safe_wrapper_with_budget, func_and_args_list)
    
    return results

def mutation_and_check(prompt, mutation_target, client):
    mutation_meta_prompt = Prompt.mutation_meta_prompt(prompt, mutation_target)
    mutation_response = generate_ans(client, mutation_meta_prompt)
    new_prompt = Prompt.parse_mutated(prompt, mutation_response, mutation_target)
    assert new_prompt.check() is None
    return new_prompt, mutation_response

def merge_and_check(prompt1, prompt2, client):
    merge_meta_prompt = Prompt.merge_meta_prompt(prompt1, prompt2)
    merge_response = generate_ans(client, merge_meta_prompt)
    merged_prompt = Prompt.parse_merged(prompt1, merge_response)
    assert merged_prompt.check() is None
    return merged_prompt, merge_response

# Wrapper function for parallel processing, creating new client in each process
def mutation_and_check_wrapper(args):
    """Wrapper function for parallel processing of mutation operations"""
    prompt, mutation_target = args
    client = create_client()
    return mutation_and_check(prompt, mutation_target, client)

def merge_and_check_wrapper(args):
    """Wrapper function for parallel processing of merge operations"""
    prompt1, prompt2 = args
    client = create_client()
    return merge_and_check(prompt1, prompt2, client)

def metric_wrapper(args):
    """Wrapper function for parallel processing of metric operations"""
    prompt, recs = args
    return metric(prompt, recs)


def generate_measure_and_rebuild_example(prompt, client):
    ANOMALY_THRES = 0.1
    consistency = 0.0
    while consistency < ANOMALY_THRES:
        for_annotation = prompt.with_content()
        annotation_response = generate_ans(client, for_annotation)
        annotations = parse_annotation(annotation_response)
        consistency = metric_full_consistency(annotations, prompt.groundtruth)
    
    prompt.rebuild_example(annotations)
    return prompt, consistency, annotations

def _metric_worker(args):
    """Worker function for metric operations"""
    _prompt, rec = args
    client = create_client()  # Create client in each process
    _prompt = copy.deepcopy(_prompt)
    _prompt.parse(rec)
    for_annotation = _prompt.with_content()
    annotation_response = generate_ans(client, for_annotation)
    consistency = 0.0
    while consistency < 0.1:
        annotations = parse_annotation(annotation_response)
        consistency = metric_full_consistency(annotations, _prompt.groundtruth)
    _prompt.rebuild_example(annotations)
    return _prompt, consistency, annotations

def metric(prompt, recs, client=None):
    res = []
    # for rec in recs:
    #     _prompt = copy.deepcopy(prompt)
    #     _prompt.parse(rec)
    #     for_annotation = _prompt.with_content()
    #     annotation_response = generate_ans(client, for_annotation)
    #     consistency = 0.0
    #     while consistency < 0.1:
    #         annotations = parse_annotation(annotation_response)
    #         consistency = metric_full_consistency(annotations, _prompt.groundtruth)
    #     _prompt.rebuild_example(annotations)
    #     res.append((_prompt, consistency, annotations))
    #parallel
    args_list = []
    
    for rec in recs:
        _prompt = copy.deepcopy(prompt)
        _prompt.parse(rec)
        args_list.append((_prompt, rec))

    with ThreadPool(processes=min(6, len(args_list))) as pool:
        results = pool.map(_metric_worker, args_list)

    for _prompt, consistency, annotations in results:
        if _prompt is not None:
            res.append((_prompt, consistency, annotations))
    
    return res



def evaluate_population(population, ori_records, client):
    """
    Evaluate where the consistency == -1
    """
    for i in range(len(population)):
        prompt, consistency = population[i]
        if consistency == -1:
            cons = []
            for _prompt, consis, annotations in metric(prompt, ori_records, client):
                cons.append(consis)
                if prompt._rec == _prompt._rec:
                    prompt = _prompt
            if len(cons) > 0:
                consistency = sum(cons) / len(cons)
            else:
                consistency = 0.0
            population.prompts[i] = prompt
            population.consistencies[i] = consistency
    return population

def parallel_evaluate_population(population, ori_records, client=None):
    """
    Evaluate the population in parallel, where the consistency == -1.
    """
    #args_list = [(prompt, ori_records) for prompt in population.prompts]
    prompts_need_evaluation_idx = [i for i, consistency in enumerate(population.consistencies) if consistency == -1]
    args_list = [(population.prompts[i], ori_records) for i in prompts_need_evaluation_idx]

    with Pool(processes=min(16, len(args_list))) as pool:
        results = pool.map(metric_wrapper, args_list)
    
    for i, consis_list in enumerate(results):
        if consis_list and len(consis_list) > 0:
            # Extract consistency values from the results
            consistencies = [item[1] for item in consis_list]
            consistency = sum(consistencies) / len(consistencies)
            # Update prompt with the first result's prompt (they should be equivalent)
            if consis_list:
                population.prompts[prompts_need_evaluation_idx[i]] = consis_list[0][0]
        else:
            consistency = 0.0
        population.consistencies[prompts_need_evaluation_idx[i]] = consistency
    
    return population

def GA(ori_records, ori_prompts, ori_number=3, generations=10, merged_nums=3, mutation_nums=2, alive=10, fathers=3, evaluation=None):
    client = create_client()
    result = MutationCache(file_path='./apo/mutations/cache_ga_test.pkl', load_existing=False)
    #1. Generate initial population by mutating original prompts with each record
    # Define mutation targets with probabilities
    mutation_targets_with_probs = [
        ('prompt_meta_behaviors', 0.2),  
        ('prompt_tips', 0.8)             
    ]
    
    def select_mutation_target():
        """Select mutation target based on probability"""
        rand_val = random.random()
        cumulative_prob = 0
        for target, prob in mutation_targets_with_probs:
            cumulative_prob += prob
            if rand_val <= cumulative_prob:
                return target
        return mutation_targets_with_probs[-1][0]  # fallback to last target

    population = Population()
    init_prompt = ori_prompts[0]
    init_prompt.parse(ori_records[0])
    population.add(init_prompt, -1)  # Add the initial prompt with a placeholder consistency
    population = parallel_evaluate_population(population, ori_records, client)
    consistencies = population.consistencies
    print(f'Original population size: {len(population)}')
    print(f'Original population consistencies: {consistencies}')
    # print initial evaluation
    if evaluation is not None:
        print(f'Initial evaluation records: {len(evaluation)}')
        _population = copy.deepcopy(population)
        _population.consistencies = [-1 for _ in range(len(_population.prompts))]  # Reset consistencies for evaluation
        _population = parallel_evaluate_population(_population, evaluation, client)
        _consistencies = _population.consistencies
        print(f'Initial evaluation consistencies: {_consistencies}')
        _population.save('./apo/mutations/evaluation_population_initial.pkl')


    if len(ori_prompts) == 1:
        ori_prompts = [copy.deepcopy(ori_prompts[0]) for _ in ori_records]
        
    # Generate args with probability-based target selection
    args = []
    for ori_record in ori_records:
        for ori_prompt in ori_prompts:
            target = select_mutation_target()
            args.append((ori_record, ori_prompt, target))
            
    random.shuffle(args)
    call_args = []
    for record, prompt, target in args:
        prompt = copy.deepcopy(prompt)
        prompt.parse(record)
        call_args.append((prompt, target))
        if len(call_args) >= ori_number:
            break
        
    # Use parallel processing to speed up the mutation process
    mutation_results = parallel_try_with_budget(mutation_and_check_wrapper, call_args)
    #filter out None results
    mutation_results = [_ for _ in mutation_results if _ is not None]
    
    for mutated_prompt, mutation_response in mutation_results:
        if mutated_prompt is not None:
            #consistency = metric_full_consistency(mutated_prompt.groundtruth, record['groundtruth'])
            population.add(mutated_prompt, -1)
            result.add(prompt, {'mutation_target': target, 'operation': 'mutation'}, mutated_prompt, mutation_response)
    
    
    #2. Evaluate the initial population
    print(f'Initial population size: {len(population)}')
    population = parallel_evaluate_population(population, ori_records)
    print(f'Initial population evaluated, size: {len(population)}')
    if evaluation is not None:
        print(f'Evaluating initial population with evaluation records, size: {len(evaluation)}')
        _population = copy.deepcopy(population)
        _population.consistencies = [-1 for _ in range(len(_population.prompts))] 
        _population = parallel_evaluate_population(_population, evaluation, client)
        _consistencies = _population.consistencies
        print(f'Initial evaluation consistencies: {_consistencies}')
        _population.save('./apo/mutations/evaluation_population_initial.pkl')
    
    
    
    population.save('./apo/mutations/initial_population.pkl')
    population.kill(alive)
    
    
    for generation in range(generations):
        #3. get top k prompts for merging
        top_prompts, top_consistencies = population.topk(min(fathers, len(population)))
        print(f'Generation {generation + 1}/{generations}, Top Consistency: {max(top_consistencies):.2f}')
        #4. randomly merge two prompts
        merging_idx = [[i, j] for i in range(len(top_prompts)) for j in range(i + 1, len(top_prompts))]
        random.shuffle(merging_idx)
        
        merged_prompts = []
        call_args = []
        for idx1, idx2 in merging_idx:
            prompt1 = top_prompts[idx1]
            prompt2 = top_prompts[idx2]
            call_args.append((prompt1, prompt2))
            if len(call_args) >= merged_nums:
                break
        
        # Use parallel processing to speed up the merging process
        print(f'Merging {len(call_args)} prompt pairs...')
        merge_results = parallel_try_with_budget(merge_and_check_wrapper, call_args)
        merge_results = [_ for _ in merge_results if _ is not None]
        
        print(f'Merging completed, {len(merge_results)} merged prompts generated.')
        print(f'Rebuilding examples for merged prompts...')
        for merged_prompt, merge_response in merge_results:
            if merged_prompt is not None:
                # randomly select a rec for further mutation
                rec_idx = random.randint(0, len(ori_records) - 1)
                merged_prompt.parse(ori_records[rec_idx])
                merged_prompt, _, _ = generate_measure_and_rebuild_example(merged_prompt, client)
                
                merged_prompts.append(merged_prompt)
                
                result.add(prompt1, {'operation': 'merge'}, merged_prompt, merge_response)
                if len(merged_prompts) >= merged_nums:
                    break
        print(f'Examples rebuilt for merged prompts, total: {len(merged_prompts)}')
            
        # get mutation_nums mutated prompts from merged prompts
        mutation_args = []
        for i in range(len(merged_prompts)):
            for j in range(len(ori_records)):
                target = select_mutation_target()
                mutation_args.append((merged_prompts[i], ori_records[j], target))
        
        for i in range(len(top_prompts)):
            for j in range(len(ori_records)):
                target = select_mutation_target()
                mutation_args.append((top_prompts[i], ori_records[j], target))

        random.shuffle(mutation_args)
        
        mutated_prompts = []
        call_args = []
        for prompt, record, target in mutation_args:
            prompt = copy.deepcopy(prompt)
            prompt.parse(record)
            call_args.append((prompt, target))
            if len(call_args) >= mutation_nums:
                break
        # Use parallel processing to speed up the mutation process
        print(f'Mutating {len(call_args)} prompts...')
        mutation_results = parallel_try_with_budget(mutation_and_check_wrapper, call_args)
        #filter out None results
        mutation_results = [_ for _ in mutation_results if _ is not None]
        
        print(f'Mutation completed, {len(mutation_results)} mutated prompts generated.')
        for mutated_prompt, mutation_response in mutation_results:
            if mutated_prompt is not None:
                mutated_prompts.append(mutated_prompt)
                result.add(prompt, {'mutation_target': target, 'operation': 'mutation'}, mutated_prompt, mutation_response)
        
        for prompt in mutated_prompts + merged_prompts:
            population.add(prompt, -1)
            
        #5. Evaluate the final population
        #population = evaluate_population(population, ori_records, client)
        print(f'Evaluating population of size {len(population)}...')
        population = parallel_evaluate_population(population, ori_records, client)
        if evaluation is not None:
            print(f'Evaluating population with evaluation records, size: {len(evaluation)}')
            _population = copy.deepcopy(population)
            _population.consistencies = [-1 for _ in range(len(_population.prompts))]  # Reset consistencies for evaluation
            _population = parallel_evaluate_population(_population, evaluation, client)
            _consistencies = _population.consistencies
            print(f'Population evaluation consistencies: {_consistencies}')
            _population.save('./apo/mutations/evaluation_population_{}.pkl'.format(generation + 1))
        
        print(f'Population evaluated, size: {len(population)}')
        #16. Save the results
        population.save('./apo/mutations/final_population_{}.pkl'.format(generation + 1))
        result.save('./apo/mutations/result_{}.pkl'.format(generation + 1))
        #7. remove the worst prompts, until the population size is alive
        population.kill(alive)
    return population

if __name__ == '__main__':
    #test_mutation(budget=10)
    #fix random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    ori_prompt = [Prompt()]
    ori_records = []
    files_train = ['AIME_1_7', 
                 'AIME_1_9', 
                 'AIME_1_5', 
                 'hmmt_c5', 
                 'hmmt_n9', 
                 'hmmt_c3',
                 'AIME_2_3',
                 'AIME_2_9',
                 'AIME_2_6', 
                 'hmmt_n1',
                 'hmmt_n3', 
                 'AIME_2_15',
                 'hmmt_g9', 
                 'hmmt_g4', 
                 'hmmt_c9'] #! split for the results in the paper
    
    test_files = ['AIME_1_11', 
                 'AIME_1_2', 
                 'AIME_1_10', 
                 'hmmt_n10', 
                 'hmmt_c8', 
                 'hmmt_c7', 
                 'AIME_2_1', 
                 'AIME_2_11', 
                 'AIME_1_14', 
                 'hmmt_n5', 
                 'hmmt_n7', 
                 'AIME_2_12', 
                 'hmmt_c10', 
                 'hmmt_g8', 
                 'hmmt_g7']
    
    
    file_base_train = []
    file_base_test = []
    file_base_path = './human_annotations/R1'
    # walk through the directory to get the full paths
    for root, dirs, files in os.walk(file_base_path):
        for file in files:
            if file.endswith('.json'):
                for f in files_train:
                    if f in file:
                        file_base_train.append(os.path.join(root, file))
                        break

    for root, dirs, files in os.walk(file_base_path):
        for file in files:
            if file.endswith('.json'):
                for f in test_files:
                    if f in file:
                        file_base_test.append(os.path.join(root, file))
                        break
                    
    for file in file_base_train:
        with open(file, 'r') as f:
            rec = json.load(f)
            ori_records.append(rec)

    population = GA(ori_records, ori_prompt, generations=4, merged_nums=4, mutation_nums=5, ori_number=10, alive=8, fathers=5, evaluation=None)
    # population = Population()
    # population.add(ori_prompt[0], -1)  # Add the initial prompt with a placeholder consistency
    test_records = []
    for file in file_base_test:
        with open(file, 'r') as f:
            rec = json.load(f)
            test_records.append(rec)
    
    for i in range(len(population)):
        population.consistencies[i] = -1  # Reset consistencies for evaluation
    
    population = parallel_evaluate_population(population, test_records)
    
    print(f'Final population size: {len(population)}')
    print(f'Final population consistencies: {population.consistencies}')
    population.save('./apo/mutations/final_population_eval.pkl')
    
    
    
