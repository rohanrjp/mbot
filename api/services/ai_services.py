import json
import re
from google import genai
from google.genai import types
from api.core.config import Config

async def generate_code_review_changes(diff_file_contents):
    client = genai.Client(api_key=Config.GEMINI_API_KEY)

    file_changes = re.findall(r"diff --git a/(\S+) b/\S+", diff_file_contents)

    prompt = f"""
    You are an AI code reviewer for GitHub pull requests. You will receive a `.diff` file containing code changes.

    ### **Instructions:**
    - Analyze the `.diff` file carefully and extract meaningful code review insights.
    - Identify issues related to performance, security, maintainability, and best practices.
    - **Most Important:** **RETURN THE CORRECT FILE NAME AND LINE NUMBER** using these rules:
      - Extract the file name from `diff --git a/<file> b/<file>`.
      - The hunk header `@@ -old_start,old_length +new_start,new_length @@` tells where changes occur.
      - Lines starting with `-` are **REMOVED** (ignore them).
      - Lines starting with `+` are **ADDED** (these need correct line numbers).
      - **Start counting from the first number after the `+` in the header** and increase it for added lines.

    #### **Expected Output for the Above Example:**
    ```json
    {{
      "summary": "Updated print statement to include formatted output.",
      "issues": [
        {{
          "file": "example.py",
          "line": 11,
          "issue": "String formatting could be unnecessary for this simple print statement.",
          "suggestion": "Consider using a simpler `print(result)` instead."
        }}
      ],
      "overall_feedback": "Good use of formatted strings, but consider simplicity."
    }}
    ```

    **Now, review the following `.diff` file carefully and follow these exact rules to determine the correct line numbers.**  

    **Files modified in this diff:**  
    {json.dumps(file_changes)}  

    **Here is the `.diff` file for review:**  
    ```
    {diff_file_contents}
    ```
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a strict and helpful AI code reviewer. Always return correct line numbers and file names.",
            max_output_tokens=800,
            top_k=2,
            top_p=0.5,
            temperature=0.3,
            response_mime_type="application/json",
            stop_sequences=["```"],
            seed=42,
        ),
    )

    if response.candidates and response.candidates[0].content.parts:
        raw_text = response.candidates[0].content.parts[0].text.strip()

        try:
            review_json = json.loads(raw_text)  
            return review_json
        except json.JSONDecodeError:
            print("Error: Model response was not valid JSON.")
            return {"error": "Model response was not valid JSON", "raw_output": raw_text}
    
    return {"error": "No valid response received from model"}