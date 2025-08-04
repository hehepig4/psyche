

PROMPT_BEST = '''# Instruction
You need to classify meta-behaviors in an inputted chain of thought (CoT) when solving a problem. Each step is enclosed by <step *>, where * is the order number of a step.
Then, you should identify the meta-behaviors by each step. Details of the task are as follows.
Meta-behaviors include:
*Analysis*: Decomposing and understanding the problem before proceeding to reasoning or evaluation.
        -       *Analysis.Problem_Definition*: Identify and clearly describe the core difficulty or central question in the problem.
        -       *Analysis.Information_Organization*: List and organize all relevant background information and known facts.
        -       *Analysis.Problem_Structuring*: Break the problem into smaller sub-problems and explain their logical connections and roles in solving the overall task.
*Inference*: Making logical deductions from known information to arrive at new conclusions. This is the core phase of reasoning.
        -       *Inference.Deductive_Reasoning*: Apply general rules or principles to derive specific conclusions relevant to the problem.
        -       *Inference.Inductive_Reasoning*: Observe specific cases and infer a general rule or trend that applies to the situation.
        -       *Inference.Abductive_Reasoning*: Given an observation, propose the most likely or plausible explanation—even if it's uncertain.
*Judgment*: Assessing different solution paths and forming final decisions based on reasoning.
        -       *Judgment.Principle_Selection*: Identify and apply the most appropriate logical principles, ethical rules, or domain-specific criteria before making a judgment or decision.
        -       *Judgment.Evaluation_of_Alternatives*: Consider multiple possible reasoning paths or hypotheses, then compare and identify the most promising one.
        -       *Judgment.Conclusion_Decision*: Make a final decision or answer based on previously completed reasoning and evaluation.
*Suggestion*: Proposing new ideas, speculative paths, or reasoning strategies that go beyond the direct content of the problem.
        -       *Suggestion.Strategic_Planning*: Develop a plan or roadmap for the reasoning steps needed to solve the problem.
        -       *Suggestion.Branch_Changing*: Switch to a different approach of reasoning or explore an alternative method when current direction seems unpromising.
        -       *Suggestion.Hypothesis_Generation*: Formulate a speculative explanation or guess based on limited evidence to guide further reasoning.
        -       *Suggestion.Analogy_Recall*: Bring in a familiar case, past experience, or known pattern to inspire a solution idea or strategy.
*Reflection*: Monitoring and evaluating the reasoning process to ensure logical correctness and coherence.
        -       *Reflection.Self_Monitoring_Evaluation*: Review the reasoning process so far. Check for gaps, mistakes, or inconsistencies in logic.
        -       *Reflection.Counterfactual_Thinking*: Consider alternative actions or decisions and speculate on what might have happened under different conditions. Used to reassess current reasoning or outcomes based on “what-if” scenarios.
        -       *Reflection.Causal_Attribution*: Analyze the reasons behind success or failure by identifying the key factors or decisions that caused the result. Supports better learning from experience.
        -       *Reflection.Strategy_Regulation*: Adjust the overall problem-solving or reasoning strategy based on feedback or prior reflection. Helps improve future performance by refining the approach.
A meta-behavior is represented hierarchically and separated by a full stop.
# Tips
Tips are the experiences and suggestions that can help you better understand the task and improve your performance.

*   **Precision in Classification & Ranking Relevance**: Ensure that the selected meta-behaviors accurately reflect the *primary* action or purpose of each step. When multiple meta-behaviors are present, prioritize the one that best describes the main goal of the step.

*   **Distinguishing Analysis and Suggestion**:
    *   `Analysis.Problem_Structuring` is used when the problem is broken down into sub-problems or its components are logically connected and defined, focusing on understanding the internal structure of the problem.
    *   `Suggestion.Strategic_Planning` involves outlining a future course of action, defining new variables, or proposing a sequence of steps to solve the problem, focusing on *how* to proceed.
    *   `Suggestion.Analogy_Recall` is appropriate when a known method, formula, past experience, or familiar case is brought up to inspire a solution idea or strategy (e.g., recalling standard mathematical techniques or drawing inspiration from a similar problem). It's for generating new ideas, not direct application of a rule.

*   **Clarifying Inference and Information Handling**:
    *   `Inference.Deductive_Reasoning` applies to direct calculations, substitutions, or the application of established formulas, rules, or logical consequences. This includes steps where information is processed or transformed based on prior knowledge or derivations. If you assume a case and then deduce its consequences, the deduction itself is `Inference.Deductive_Reasoning`.
    *   `Suggestion.Hypothesis_Generation` is used when formulating a *speculative explanation or unproven assumption* to explore a potential path.
    *   `Analysis.Information_Organization` is primarily for listing, re-stating, or organizing *given* or *known* facts (including existing equations or derived facts) for clarity or further use, without new deductions or transformations.

*   **Identifying and Refining Reflection**:
    *   `Reflection.Self_Monitoring_Evaluation` is crucial for steps where the model reviews its own reasoning process so far, checking for gaps, mistakes, inconsistencies in logic, or considering if the current path is effective. Look for phrases like "Wait," "Let me think," "Check for gaps," or "Doesn't match."
    *   If this reflection leads to a significant change in the problem-solving method, `Suggestion.Branch_Changing` should also be considered.
    *   When a re-evaluation leads to a new way of breaking down or approaching the problem's structure, `Analysis.Problem_Structuring` might be the primary meta-behavior.
    *   `Reflection.Strategy_Regulation` involves adjusting the *overall problem-solving approach* based on feedback or prior reflection.
    *   `Reflection.Causal_Attribution` is specifically for analyzing the *reasons* behind a particular outcome or result, often after a success or failure, to learn from experience.

*   **Applying Principles and Evaluating Alternatives (Judgment)**:
    *   `Judgment.Principle_Selection` is appropriate when recalling and applying a known mathematical identity, theorem, or established rule to proceed with the solution.
    *   `Judgment.Evaluation_of_Alternatives` is for comparing and assessing multiple possible reasoning paths or hypotheses to choose the most promising one.
# Task
**You should select all relevant meta-behaviors, ranking them and separating them by semicolon in descending order based on their relevance and importance.**
All the meta-behaviors are not exclusive, and a step may contain multiple meta-behaviors.
Also, these meta-behaviors may belong to a same type but with different sub-types, like *Analysis.Problem_Definition* and *Analysis.Problem_Structuring*, etc.
You should choose all the meta-behaviors that are possible in this step.
**To provide a precise and faithful answer, you need to fully utilize the semantic connection between consecutive steps.**
# Output Format
**You need to strictly output in the following format**:
<step 1> meta-behavior(s) </step 1>
<step 2> meta-behavior(s) </step 2>
...
<step n> meta-behavior(s) </step n>
# Input
## The problem
{problem_desc}
## The long CoT
{CoT}
# Output
'''

PROMPT_ORIGINAL = '''# Instruction
You need to classify meta-behaviors in an inputted chain of thought (CoT) when solving a problem. Each step is enclosed by <step *>, where * is the order number of a step. 
Then, you should identify the meta-behaviors by each step. Details of the task are as follows.
Meta-behaviors include:
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
# Task
**You should select all relevant meta-behaviors, ranking them and separating them by semicolon in descending order based on their relevance and importance.**
All the meta-behaviors are not exclusive, and a step may contain multiple meta-behaviors.
Also, these meta-behaviors may belong to a same type but with different sub-types, like *Analysis.Problem_Definition* and *Analysis.Problem_Structuring*, etc.
You should choose all the meta-behaviors that are possible in this step.
**To provide a precise and faithful answer, you need to fully utilize the semantic connection between consecutive steps.**
# Output Format
**You need to strictly output in the following format**:
<step 1> meta-behavior(s) </step 1>
<step 2> meta-behavior(s) </step 2>
...
<step n> meta-behavior(s) </step n>
# Input
## The problem
{problem_desc}
## The long CoT
{CoT}
# Output
'''