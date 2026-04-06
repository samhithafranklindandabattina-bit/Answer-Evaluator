import json
from pdf_to_answer_dict import pdf_dict_streamlit
from AnswerToMarks import Grader
import os

# 🔧 Fix for torch + streamlit conflict
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

def main(pdf_path: str, answer_key_path: str, api_key: str):
    """
    Extracts answers from a scanned PDF, grades them using semantic similarity, 
    and returns marks for each question.

    Args:
        pdf_path (str): Path to the scanned PDF file.
        api_key (str): API key for OCR/NLP services.
        answer_key_path (str): Path to the JSON file containing correct answers.

    Returns:
        dict: A dictionary mapping question numbers to assigned marks.
    """
    # Step 1: Extract student answers from PDF
    print("Extracting answers from PDF...")
    student_answers = pdf_dict_streamlit(pdf_path, api_key)
    print(student_answers)

    # Step 2: Load the answer key from a JSON file
    print("Loading correct answers...")
    with open(answer_key_path, "r", encoding="utf-8") as file:
        answer_key = json.load(file)

    # Step 3: Initialize Grader and grade answers
    print("Grading answers...")
    grader = Grader()
    print("ans:",student_answers, answer_key)
    scores = grader.grade_answer(student_answers, answer_key)

    # Step 4: Print and return the result
    print("Grading complete! Scores:", scores)
    return scores

import json

def main_st(pdf_file, answer_key_file, api_key):
    """
    Extracts answers from an open PDF file, grades them using semantic similarity, 
    and returns marks for each question.

    Args:
        pdf_file (file-like object): Opened PDF file (BytesIO from Streamlit).
        answer_key_file (file-like object): Opened JSON file (BytesIO from Streamlit).
        api_key (str): API key for OCR/NLP services.

    Returns:
        dict: A dictionary mapping question numbers to assigned marks.
    """
    # Step 1: Extract student answers from PDF
    print("Extracting answers from PDF...")
    student_answers = pdf_dict_streamlit(pdf_file, api_key)

    # Step 2: Load the answer key from the JSON file-like object
    print("Loading correct answers...")
    answer_key_file.seek(0)
    answer_key = json.load(answer_key_file)  # Directly read JSON from BytesIO

    # Step 3: Initialize Grader and grade answers
    print("Grading answers...")
    grader = Grader()
    scores = grader.grade_answer(student_answers, answer_key)

    # Step 4: Print and return the result
    print("Grading complete! Scores:", scores)
    return scores


# Example Usage
if __name__ == "__main__":
    pdf_file = r"test_assignments\test_ans_sheet.pdf"  
    answer_key_file = r"test_assignments\ans_key.json"  
    
