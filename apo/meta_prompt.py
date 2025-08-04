MUTATION_META_PROMPT = '''# Instruction:
You are an expert in prompt engineering.
The following five prompts describe a task.
You will also be given an example of a response to this prompt.
Your task is to mutate and improve a specific part of the prompt, based on the example and answer, according to the following rules:
(1) Review the task in the prompt to understand the key objectives and requirements that the instruction needs to address.
(2) Focus on the part of the prompt indicated by the <part> tag that needs mutation.
(3) Analyse the example and answer to identify any gaps, ambiguities or areas for improvement in the prompt.
(4) Maintain the original format and structure of the prompt while enhancing clarity, specificity and guidance in the mutated part.
(5) Ensure that the output format of the mutated part is consistent with the original prompt structure.
(6) Do not modify the names of meta-behaviors or the structure of the prompt.
(7) Tags (e.g., in <>) should not be modified.
(8) All names of meta-behaviors (xx.xx) should be strictly retained as they are, except for their descriptions, which can be modified for clarity. And, no addition and deletion of meta-behaviors is allowed.
(9) Particularly, some absent fields in the example typically indicate that the original response is with incorrect format, try to fix it.
(10) Especially, tips, including details of meta-behaviors and tasks, are more flexible and can be modified to better fit the merged prompt.
(11) Notice that, example is not available when the following prompt is used for downstream tasks.

Output the specific mutated part in the <mutated_part> tag after providing a comprehensive, step-by-step thinking, as follows:
**Output format: <mutated_part> Mutated and improved part of the prompt </mutated_part>**

<prompt_header> {prompt_header} </prompt_header>
<prompt_meta_behaviors> {prompt_meta_behaviors} </prompt_meta_behaviors>
<prompt_tips> {prompt_tips} </prompt_tips>
<prompt_task_description> {prompt_task_description} </prompt_task_description>
<prompt_format_description> {prompt_format_description} </prompt_format_description>
<prompt_input_organization> {prompt_input_organization} </prompt_input_organization>


# Example
{example}

# Mutation Target
{part_name}

'''


MERGE_META_PROMPT = '''# Instruction
You are an expert in prompt engineering.
You will be given two prompts, each consisting of five parts that describe a task.
Each prompt is optimized based on an example of the task.
Your task is to combine these two prompts to create a single, coherent prompt that retains the strengths of both while ensuring clarity and consistency.
Focus on the following aspects:
(1) Identify the key objectives and requirements in both prompts.
(2) Combine the relevant parts from both prompts to create a comprehensive and clear merged prompt.
(3) Maintain the original format and structure of the prompts, enhancing clarity, specificity and guidance where necessary.
(4) Ensure the merged prompt is logically consistent and flows well.
(5) The output format should be consistent with the original prompt structure.
(6) Do not modify the names of meta-behaviors or the structure of the prompt.
(7) Tags (e.g., in <>) should not be modified.
(8) All names of meta-behaviors (xx.xx) should be strictly retained as they are, except for their descriptions, which can be modified for clarity. And, no addition and deletion of meta-behaviors is allowed.
(9) The consideration aspects of both prompts may vary, so you should carefully merge them to ensure that the final prompt is comprehensive.
(10) Especially, tips, including details of meta-behaviors and tasks, are more flexible and can be modified to better fit the merged prompt.

Output the merged prompt with the five tags after providing comprehensive step-by-step reasoning as follows:
**Output format:**
<prompt_header> Merged and optimized prompt header </prompt_header>
<prompt_meta_behaviors> Merged and optimized meta-behaviors </prompt_meta_behaviors>
<prompt_tips> Merged and optimized tips </prompt_tips>
<prompt_task_description> Merged and optimized task description </prompt_task_description>
<prompt_format_description> Merged and optimized format description </prompt_format_description>
<prompt_input_organization> Merged and optimized input organization </prompt_input_organization>


# Prompt 1
<prompt_header> {prompt_header_1} </prompt_header>
<prompt_meta_behaviors> {prompt_meta_behaviors_1} </prompt_meta_behaviors>
<prompt_tips> {prompt_tips_1} </prompt_tips>
<prompt_task_description> {prompt_task_description_1} </prompt_task_description>
<prompt_format_description> {prompt_format_description_1} </prompt_format_description>
<prompt_input_organization> {prompt_input_organization_1} </prompt_input_organization>

# Prompt 2
<prompt_header> {prompt_header_2} </prompt_header>
<prompt_meta_behaviors> {prompt_meta_behaviors_2} </prompt_meta_behaviors>
<prompt_tips> {prompt_tips_2} </prompt_tips>
<prompt_task_description> {prompt_task_description_2} </prompt_task_description>
<prompt_format_description> {prompt_format_description_2} </prompt_format_description>
<prompt_input_organization> {prompt_input_organization_2} </prompt_input_organization>


'''