PROMPT_HEADER = '''# Instruction
You need to classify meta-behaviors in an inputted chain of thought (CoT) when solving a problem. Each step is enclosed by <step *>, where * is the order number of a step. 
Then, you should identify the meta-behaviors by each step. Details of the task are as follows.'''


META_BEHAVIORS = '''Meta-behaviors include:
*Analysis*: Decomposing and understanding the problem before proceeding to reasoning or evaluation.
	-	*Analysis.Problem_Definition*: Identify and clearly describe the core difficulty or central question in the problem.
	-	*Analysis.Information_Organization*: List and organize all relevant background information and known facts.
	-	*Analysis.Problem_Structuring*: Break the problem into smaller sub-problems and explain their logical connections and roles in solving the overall task.
*Inference*: Making logical deductions from known information to arrive at new conclusions. This is the core phase of reasoning.
	-	*Inference.Deductive_Reasoning*: Apply general rules or principles to derive specific conclusions relevant to the problem.
	-	*Inference.Inductive_Reasoning*: Observe specific cases and infer a general rule or trend that applies to the situation.
	-	*Inference.Abductive_Reasoning*: Given an observation, propose the most likely or plausible explanation—even if it's uncertain. 
*Judgment*: Assessing different solution paths and forming final decisions based on reasoning.
	-	*Judgment.Principle_Selection*: Identify and apply the most appropriate logical principles, ethical rules, or domain-specific criteria before making a judgment or decision.
	-	*Judgment.Evaluation_of_Alternatives*: Consider multiple possible reasoning paths or hypotheses, then compare and identify the most promising one.
	-	*Judgment.Conclusion_Decision*: Make a final decision or answer based on previously completed reasoning and evaluation.
*Suggestion*: Proposing new ideas, speculative paths, or reasoning strategies that go beyond the direct content of the problem.
	-	*Suggestion.Strategic_Planning*: Develop a plan or roadmap for the reasoning steps needed to solve the problem.
	-	*Suggestion.Branch_Changing*: Switch to a different approach of reasoning or explore an alternative method when current direction seems unpromising.
	-	*Suggestion.Hypothesis_Generation*: Formulate a speculative explanation or guess based on limited evidence to guide further reasoning.
	-	*Suggestion.Analogy_Recall*: Bring in a familiar case, past experience, or known pattern to inspire a solution idea or strategy.
*Reflection*: Monitoring and evaluating the reasoning process to ensure logical correctness and coherence.
	-	*Reflection.Self_Monitoring_Evaluation*: Review the reasoning process so far. Check for gaps, mistakes, or inconsistencies in logic.
	-	*Reflection.Counterfactual_Thinking*: Consider alternative actions or decisions and speculate on what might have happened under different conditions. Used to reassess current reasoning or outcomes based on “what-if” scenarios.
	-	*Reflection.Causal_Attribution*: Analyze the reasons behind success or failure by identifying the key factors or decisions that caused the result. Supports better learning from experience.
	-	*Reflection.Strategy_Regulation*: Adjust the overall problem-solving or reasoning strategy based on feedback or prior reflection. Helps improve future performance by refining the approach.
A meta-behavior is represented hierarchically and separated by a full stop. 
'''

TASK_DESCRIPTION = '''
# Task
**You should select all relevant meta-behaviors, ranking them and separating them by semicolon in descending order based on their relevance and importance.**
All the meta-behaviors are not exclusive, and a step may contain multiple meta-behaviors.
Also, these meta-behaviors may belong to a same type but with different sub-types, like *Analysis.Problem_Definition* and *Analysis.Problem_Structuring*, etc.
You should choose all the meta-behaviors that are possible in this step.
**To provide a precise and faithful answer, you need to fully utilize the semantic connection between consecutive steps.**
'''

FORMAT_DESCRIPTION = '''
# Output Format
**You need to strictly output in the following format**:
<step 1> meta-behavior(s) </step 1>
<step 2> meta-behavior(s) </step 2>
...
<step n> meta-behavior(s) </step n>
'''

INPUT_ORGANIZATION = '''
# Input
## The problem
{problem_desc}
## The long CoT
{CoT}
# Output
'''

EXAMPLE_ORGANIZATION = '''
# Example
Typically, the results in <attempt step_id> </attempt step_id> are your previous attempt and <answer step_id> </answer step_id> is the answer annotation for the current step.
It is important to learn from the example, particularly the differences between the previous attempt and the answer annotation, in order to improve your annotation for the next task.

## Example question: {question}

## Example CoT: {reasoning}

## Example Annotation: {example}
'''

TIPS = '''
# Tips
Tips are the experiences and suggestions that can help you better understand the task and improve your performance.
'''