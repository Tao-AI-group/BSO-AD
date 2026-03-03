import requests
import pandas as pd
import re
import json
import os
import random
import argparse
from tqdm import tqdm
import argparse

"""
    Prompt types required: 
    Prompt 1: Binary (level 1:for determining whether the given abstract has the specific BSSR factor (1 or 7) (zero-shot; definition))
    Prompt 2: Multi-class (level 2: within the specific category, determine which level 2 class; few shot (give examples))

    Outcome:
    Prompt 1:- Classify + Tag + explanation + evidence: Whether the abstract has the level 1 concept; if it does, extract it and associated ADRD disorder
    Prompt 1:- Classify only + explanation + evidence: Given the abstract and the level 1 concept, further refine the entity tag to finer categories [level 2 classes] and related ADRD entity
    """

def create_prompt1(paper_id, title, abstract, factor, explanation_length = 10):

    sys_inst = f"""
    ## Context:
        You are an expert in Behavioral and Social Science Research (BSSR), which involves the systematic study of how behaviors and social factors influence health. 
        The BSSR factors can be categorized into 7 classes: 
        (1) Behavior and Lifestyle, such as physical activity, substance use, sleep, spirituality and religion; 
        (2) Food, such as food access, diet, and food security; 
        (3) Economic Stability. Examples: employment, expense, income, socioeconomic status; 
        (4) Neighborhood. Examples: physical environment, geographic location, social-environmental neighborhood; 
        (5) Social and community context. Examples: culture, social isolation, social support, culture; 
        (6) Education and Literacy. Examples: access to education, literacy, education quality; 
        (7) Healthcare. Examples: healthcare access, quality of healthcare, healthcare payment.
        Please do not limit yourself to the provided examples.  
        
        Currently, you are focusing on investigating **the documented impact of {factor} factors on Alzheimer's disease and related dementias (ADRD)**.
        """
    prompt = f"""
    ## Requirements:
    Your task is to extract ADRD-related {factor} entities (single or multiple word phrases) and associated sentences from PubMed abstracts. 

    ## Format:
    - Factor Relevance: Classify whether the given PubMed abstract represents a study on the **impact of {factor} on ADRD**
    - Next, identify potential entities for:
    i. {factor} factors and
    ii. AD/ADRD
    - For each extracted entity:
    i. Provide the source sentence that shows the association between {factor} and ADRD
    ii. Give an explanation **within {explanation_length}** words justifying the relevance of the entity.

    ## Quality: 
    - While assessing factor relevance, **ensure that the extracted entities are NOT related to symptoms, medications, genes, etc. related to ADRD when factor_relevance is No**.
    - Solely focus on the **documented impact of the BSSR factor: {factor} on ADRD** 
    - Only extract **entities associated with ADRD**. Ignore sentences that read like background or general related information.
    - DO NOT hallucinate or change the names of entities or categories, as well as the source sentence.
    - Make your assessments **solely based on the information contained in the given Data (title and abstract)**.
    
            
    ## Output:
    
    Here is an example of template for the output. **DO NOT return any other text other than the output json**.
    ```json
    {{
    "paper_PMID": "<PMID>",
    "factor_relevance":<whether relevant to {factor}--Yes/No>
    "potential_entities": [{{
    "entity_name": <the entity name>,
    "source_sentence": <sentence evidence from the PubMed abstract>,
    "category": <assigned category -- ADRD/{factor}>,
    "explanation":<justification for annotation>}},
    ...
    {{
    ...
    }}
    ]
    }}
    
    ## Data:
    Paper ID: {paper_id}
    Title: {title}
    Abstract: {abstract}

    """
    return sys_inst, prompt

def create_prompt2(paper_id, title, abstract, factor, entity_name, source_sentence, classes_list, examples, explanation_length=10):
    sys_inst = f"""
        ## Context:
            You are an expert in Behavioral and Social Science Research (BSSR), which involves the systematic study of how behaviors and social factors influence health. 
            Currently, you are focusing on investigating **the documented impact of {factor} factors on Alzheimer's disease and related dementias (ADRD)**.
            **Data**: As input, you will be given the following:
            - **PubMed title**
            - **PubMed abstract**
            - **{factor} related entity**
            - **source sentence which contains the entity**
        ## Use Case: Your task is to classify the ADRD-related {factor} entity (single or multi word phrases) using the associated sentence into one of the following classes based on the provided definitions:
          {"\n \t".join(["- "+i for i in classes_list+["Undefined: Not classified under existing behavioral or social factor labels."]])}

            """
    prompt = f"""
        ## Format:
        - **Factor Relevance**: Verify whether the given entity **truly represents {factor} factor**
        - **Factor class**: Classify the entity in the source sentence in **one or more** of the given classes. If the entity cannot be classified into any of the classes, classify it as "Undefined" 
        - **Explanation**: Give an explanation **within {explanation_length}** words justifying the relevance of the entity to the assigned class.

        ## Quality:
        - While verifying factor relevance, **ensure that the extracted entities are NOT related to symptoms, medications, genes, etc. related to ADRD**.
        - Solely focus on the **documented impact of the BSSR factor: {factor} on ADRD** 
        - Only extract **entities associated with ADRD**. Ignore sentences that read like background or general related information.
        - DO NOT hallucinate or change the names of entities or categories, as well as the source sentence.
        - Make your assessments **solely based on the information contained in the given Data**.

        ## Examples:
        Below are a few examples of **Factor class** classification. **Note that if an entit/sentence can be assigned to a factor class, then the **factor relevance** must be **Yes**.

        {examples}
   
        ## Output:
    
        Here is an example of template for the output. **DO NOT return any other text other than the output json**.
        ```json
        {{
        "paper_PMID": "<PMID>",
        "entity_name": "<entity name>",
        "source_sentence": "<sentence evidence>",
        "factor_relevance":"<Yes/No>"
        "factor_class": ["<factor class label 1>", "<factor class label 2>"],
        "explanation":"<justification for annotation>",
        }}
        
        ## Data:
        Paper ID: {paper_id}
        Title: {title}
        Abstract: {abstract}
        Entity name: {entity_name}
        Source sentence: {source_sentence}

        """
    return sys_inst, prompt

def query(sys_prompt, content_prompt, API_URL=None, MODEL_NAME=None):
    headers = {"Content-Type": "application/json",}
    
    payload = {
       "model": MODEL_NAME, 
       "messages": [
           {"role": "system", "content":sys_prompt},
           {"role": "user", "content": content_prompt}
       ],
       "temperature": 0,
       "top_p":0.9,
       }
    
    resp = requests.post(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    output = resp.json()["choices"][0]["message"]["content"]
    return output

def parse_binaryEntity(llm_response):
    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    records = []

    if json_match:
        try:
            data = json.loads(json_match.group())
            pmid = data.get("paper_PMID", "")
            relevance = data.get("factor_relevance", "")
            entities = data.get("potential_entities", [])

            if entities:
                for entity in entities:
                    records.append({
                        "PMID": pmid,
                        "factor_relevance": relevance,
                        "entity": entity.get("entity_name", ""),
                        "category": entity.get("category", "").replace(" ","_"),
                        "source_sentence": entity.get("source_sentence", ""),
                        "explanation": entity.get("explanation", "")
                    })
            else:
                records.append({
                    "PMID": pmid,
                    "factor_relevance": relevance,
                    "entity": "",
                    "category": "",
                    "source_sentence": "",
                    "explanation": ""
                })

        except Exception as e:
            print("Error:", e)
            print(llm_response)
    else:
        print("No JSON block found in LLM output.")
    return records

def parse_multiclass(llm_response):
    json_blocks = re.findall(r'\{[^{}]*\}', llm_response, re.DOTALL)
    parsed_objects = []
    seen = set()

    for block in json_blocks:
        try:
            # Parse JSON block
            data = json.loads(block)

            # Canonical string to detect duplicates
            canonical = json.dumps(data, sort_keys=True)
            if canonical in seen:
                continue  # skip duplicate
            seen.add(canonical)
            factor_class_labels = data.get("factor_class",[])
            factor_class_labels = [i.replace(" ",'_') for i in factor_class_labels]

            # Format result
            result = {
                "PMID": data.get("paper_PMID", ""),
                "entity_name": data.get("entity_name", ""),
                "factor_relevance": data.get("factor_relevance", ""),
                "factor_class": factor_class_labels,
                "source_sentence": data.get("source_sentence", ""),
                "explanation": data.get("explanation", "")
            }
            parsed_objects.append(result)

        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
            print("Offending block:", block)
            continue

    # If no valid JSON blocks found, return one empty object
    if not parsed_objects:
        return [{
            "PMID": "",
            "entity_name": "",
            "factor_relevance": "",
            "factor_class": [],
            "source_sentence": "",
            "explanation": ""
        }]
    return parsed_objects

def part1_EntityTagging(args):
    API_URL = f"http://localhost:{args.port}/v1/chat/completions"
    MODEL_NAME = model_name_id_mapping[args.model]
    factor = BSSR_factors_dict[args.factor_num]
    factor_id = factor.replace(" ","_")
    input_path = "./version2/screening/included_articles-08062025.xlsx" #path to file with screened articles
    output_path = "./version2/extraction_classification"

    df = pd.read_excel(input_path, engine='openpyxl')
    df = df[["PMID", "Title", "Abstract"]].dropna()

    all_data=[]
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing articles"):
        paper_id = str(row["PMID"])
        title = str(row["Title"])
        abstract = str(row["Abstract"]).strip()
        sys_prompt, content_prompt = create_prompt1(paper_id, title, abstract, factor)
        output = query(sys_prompt, content_prompt, API_URL, MODEL_NAME)
        result = parse_binaryEntity(output)
        if result:
            if idx<3:
                print(result)
            all_data.extend(result)

    df_out = pd.DataFrame(all_data)
    df_out.to_csv(f"{output_path}/{args.model}-{factor_id}-part1.csv",index=False)

def get_FewShot_examples(factor_id,num_examples):
    with open("./version2/info/examples.json") as fj:
        data = json.load(fj)
    example_data=[]
    for factor_class,samples in data[factor_id].items():
        if len(samples)>num_examples:
            sample = random.sample(samples,num_examples)
        else:
            sample = samples
        for entry in sample:
            formatted_sample = f"""
            Source_sentence: {entry},
            Factor Class: {factor_class}
            """
            example_data.append(formatted_sample)
    examples = "\n".join(example_data)
    return examples

def part2_MultiLabelLevel2(args):
    API_URL = f"http://localhost:{args.port}/v1/chat/completions"
    MODEL_NAME = model_name_id_mapping[args.model]
    factor = BSSR_factors_dict[args.factor_num]
    factor_id = factor.replace(" ","_")
    input_path = "./version2/screening/included_articles-08062025.xlsx"
    output_path = "./version2/extraction_classification"

    df = pd.read_excel(input_path, engine='openpyxl')
    df = df[["PMID", "Title", "Abstract"]].dropna()
    df = df.set_index("PMID")

    with open("./version2/info/definitions.json") as fj:
        definitions = json.load(fj)
    classes_list = [f"{key.replace("_"," ")}: {value}" for key,value in definitions[factor_id].items()]
    examples = get_FewShot_examples(factor_id,args.num_examples)
    
    #######################################################################
    df_in = pd.read_csv(f"{output_path}/{args.model}-{factor_id}-part1.csv")

    x = df_in[df_in["factor_relevance"]=="Yes"]
    df_x = x[x["category"]==f"{factor_id}"].reset_index()

    all_results = []
    for idx,row in df_x.iterrows():
        print(idx)
        paper_id = row["PMID"]
        title = df.loc[paper_id]["Title"]
        abstract = df.loc[paper_id]["Abstract"]
        entity_name = row["entity"]
        source_sent = row["source_sentence"]
        sys_prompt, content_prompt = create_prompt2(paper_id, title, abstract, factor, entity_name, source_sent, classes_list, examples)
        output = query(sys_prompt, content_prompt, API_URL, MODEL_NAME)
        res = parse_multiclass(output)
        if res!=None:
            if idx<3:
                print(res)
            all_results.extend(res)

    df_write = pd.DataFrame(all_results)
    df_write.to_csv(f"{output_path}/{args.model}-{factor_id}-part2.csv",index=False)


BSSR_factors_dict={0:"Behavior and Lifestyle", 
                   1:"Economic stability", 
                   2:"Education and Literacy", 
                   3:"Food", 
                   4:"Healthcare", 
                   5:"Neighborhood", 
                   6:"Social and Community"}

model_name_id_mapping = {"medgemma": "google/medgemma-27b-text-it",
                        "llama4": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                        "qwen3":"Qwen/Qwen3-32B"}

def main():
   parser = argparse.ArgumentParser(description="Ontology evaluation tagging and mapping")
   parser.add_argument("--model", type=str, help="Name of the input LLM")
   parser.add_argument("--port", type=int, default=8000, help="Port number of vLLM")
   parser.add_argument("--factor_num", type=int, default=0, help="Select the desired BSSR factor number (0-6)")
   parser.add_argument("--num_examples", type=int, default = 4, help="Number of few-shot examples")
   parser.add_argument("--task", type=int, default=0, help="Choice of task--0(both), 1(part1), 2(part2)")
   args = parser.parse_args()
   
   BSSR_category = BSSR_factors_dict[args.factor_num]
   BSSR_id = BSSR_category.replace(" ","_")

   out1 = f"./version2/extraction_classification/{args.model}-{BSSR_id}-part1.csv"
   out2 = f"./version2/extraction_classification/{args.model}-{BSSR_id}-part2.csv"
   
   do = lambda f, o: f(args) if not os.path.exists(o) else None
   if args.task in (0, 1): 
       do(part1_EntityTagging, out1)
   if args.task in (0, 2): 
       do(part2_MultiLabelLevel2, out2)
   
    
if __name__ == "__main__":
   main()