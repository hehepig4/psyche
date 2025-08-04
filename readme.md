# LLM-as-annotators. 
Code in `./classify`, where:
- `anot.py` is the main script for annotation.
- `parse.py` contains functions to parse the input data.
- `prompt.py` defines the prompts used for classification.
- `config.py` holds configuration settings and prompts.
- `merge.py` parses and merges annotations from multiple models.
- *`statistics.ipynb` and `post_check_draw.py` used for statistical analysis of the annotations, generating figures in the paper*. 

Running anot.py -> merge.py -> statistics.ipynb.
# CAPO. 
Code in `./apo`, where:  
- `main.py` is the main script for running the CAPO process.  
- `prompt.py` and `meta_prompt.py` define the prompts used in the CAPO process.  
- `mutations/` contains the objects in the paper, where `_eval.pkl` store the consistencies on test set.  
# Data. 
## Files. 
- Raw machine-annotated data is omitted, directly refer to the annotated files. 
- Machine-annotated data is in `machine_annotations/`. 
- Human-annotated data is under `human_annotations/`. 
- Post-answer-check data is in `post_answer_check_data/`.
## Data format.
Except the meta-data from original AIME and Human data, the data format is unified as follows:
```json
{
    "reasoning": raw reasoning content,
    "question": question content,
    "True Answer": true answer content,
    "steps": {
        "reasoning": {
            "1": {
                "gemini-best_flag": [
                    mental processes identified from LLM-annotators
                ],
                "content": reasoning content,
                "human_anot": [
                    mental processes identified from human annotators if available
                ]
            },
        ...
        "gemini-best_response": Annotation response from the model, 
        },
    }
}