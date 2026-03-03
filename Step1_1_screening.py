import requests
import pandas as pd
import re
import json
import argparse
from tqdm import tqdm
import datetime

def create_prompt(paper_id, title, abstract):
  sys_inst = "You are a subject matter expert in Psychiatry supporting the screening of research literature."

  prompt = f"""
  Instructions:
  Your task is to evaluate each candidate paper (based on the given title and abstract) against the following three criteria:
  1. AD/ADRD Focus:  The study must focus on Alzheimer's Disease or related dementias (AD/ADRD), including but not limited to: Alzheimer Disease, Primary Progressive Aphasia, Primary Progressive Nonfluent Aphasia, Vascular Dementia, CADASIL, Multi-Infarct Dementia, Frontotemporal Lobar Degeneration, Frontotemporal Dementia, Primary Progressive Nonfluent Aphasia, Huntington Disease, Lewy Body Disease, Mixed Dementias.
  2. Behavioral and Social Factors Focus: The study must explore the relationship between AD/ADRD and behavioral or social factors (e.g., behavioral symptoms, social determinants of health, interpersonal relationships, caregiver burden).
  3. Human study: The study must involve human participants or data. Exclude studies based exclusively on animal models.
  
  Output:
  For each criterion, return only 'true' or 'false' for each of the criterion. Next, provide a final decision ('include' or 'exclude') along with a brief explanation. Make your assessments solely based on the information contained in the title and abstract.
  Use the exact output format below:
  {{
      "paper_id": "<your paper ID here>",
      "ADRD_focus": true/false,
      "behavior_social_focus": true/false,
      "human_study": true/false,
      "final_decision": {{
          "include": true/false,
          "reason": "..."
          }}
  }}
  
  Input:
  Paper ID: {paper_id}
  Title: {title}
  Abstract: {abstract}
  """
  return sys_inst, prompt

def query_llm(paper_id, title, abstract, API_URL, MODEL_NAME):
    sys_prompt, content_prompt = create_prompt(paper_id, title, abstract)
    headers = {"Content-Type": "application/json",}

    payload = {
        "model": MODEL_NAME,  
        "messages": [
            {"role": "system", "content":sys_prompt},
            {"role": "user", "content": content_prompt}
        ],
        "temperature": 0,
        "top_p":0.9,
        "max_tokens":2048,
        }

    resp = requests.post(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    output = resp.json()["choices"][0]["message"]["content"]
    json_match = re.search(r'\{.*\}', output, re.DOTALL)
    try:
        parsed = json.loads(json_match.group())
        results_parsed = {
            "PMID": parsed.get("paper_id", paper_id),
            "ADRD_focus": parsed.get("ADRD_focus", None),
            "behavior_social_focus": parsed.get("behavior_social_focus", None),
            "human_study": parsed.get("human_study", None),
            "include": parsed.get("final_decision", {}).get("include", None),
            "reason": parsed.get("final_decision", {}).get("reason", "")
        }
    except Exception as e:
        print(f"[Error] PMID {paper_id}: {e}")
        results_parsed = {
            "PMID": paper_id,
            "ADRD_focus": None,
            "behavior_social_focus": None,
            "human_study": None,
            "include": None,
            "reason": f"LLM or JSON error: {e}"
        }
    return results_parsed

def run_inference(args):
    current_date = datetime.datetime.now()
    date = current_date.strftime("%m%d%Y")

    lm = args.lm
    API_URL = f"http://localhost:{args.port}/v1/chat/completions"
    MODEL_NAME = args.model_id
    output_file = f"{args.output_path}/{lm}_results-{date}.csv"
    input_path = args.input_path ##expects a .csv file in a directory

    df = pd.read_excel(input_path, engine='openpyxl')
    df = df[["PMID", "Title", "Abstract"]].dropna()

    results = []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing articles"):
        paper_id = str(row["PMID"])
        title = str(row["Title"])
        abstract = str(row["Abstract"]).strip()

        llm_response = query_llm(paper_id, title, abstract, API_URL, MODEL_NAME)
        if idx<3:
            print(llm_response)
        results.append(llm_response)
    
    df = pd.DataFrame(results)
    df.to_csv(output_file,index=False)

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="A script to screen abstracts for inclusion.")

    # Add arguments
    parser.add_argument("--lm", type=str, help="Name of the input LLM")
    parser.add_argument("--port", type=int, help="Port number of vLLM")
    parser.add_argument("--model_id", type=str, help="Huggingface model ID")
    parser.add_argument("--output_path", type=str, help="path to output directory")
    parser.add_argument("--input_path", type=str, help="Path to input excel file")

    # Parse the arguments
    args = parser.parse_args()
    run_inference(args)


    

if __name__ == "__main__":
    main()