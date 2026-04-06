from sentence_transformers import SentenceTransformer, util
import math

class Grader:
    """
    A class to grade textual answers based on their semantic similarity to correct answers 
    using a pre-trained language model.
    """

    def __init__(self):
        """
        Initializes the Grader with a pre-trained SentenceTransformer model for generating text embeddings.
        """
        # Load a lightweight, pre-trained model "all-MiniLM-L6-v2" to convert text into numerical embeddings
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embeddings(self, text: str):
        """
        Converts a given text into a numerical embedding (vector representation) using the model.

        Args:
            text (str): The text to be converted into an embedding.

        Returns:
            tensor: A PyTorch tensor representing the embedding of the text.
        """
        # Encode the text into an embedding using the pre-trained model and return it as a tensor
        return self.model.encode(text, convert_to_tensor=True)

    def find_similarity(self, answer_text, answer_key) -> float:
        """
        Calculates the cosine similarity between two embeddings to measure their semantic similarity.

        Args:
            answer_text (tensor): Embedding of the student's answer.
            answer_key (tensor): Embedding of the correct answer.

        Returns:
            float: A similarity score between 0 and 1, where 1 means identical meaning.
        """
        # Compute cosine similarity between the embeddings and extract the scalar value
        return util.pytorch_cos_sim(answer_text, answer_key).item()

    def grade_answer(self, input_json: dict, answer_key_json: dict) -> dict:
        """
        Grades the student's answers by comparing them to the answer key and assigns scores based on similarity.

        Args:
            input_json (dict): A dictionary of student answers where keys are question identifiers and values are the answer texts.
            answer_key_json (dict): A dictionary of correct answers with max marks, where keys are question identifiers and values are dictionaries containing "answer" and "Max Marks".

        Returns:
            dict: A dictionary with scores for each answer.
        """
        score_dict = {}  # Dictionary to store the calculated scores
        for key, value in input_json.items():
            if key in answer_key_json:  # Ensure the question exists in the answer key
                # Extract student's answer (value is the answer text directly)
                student_answer = value
                # Extract the correct answer using the correct key "answer"
                correct_answer = answer_key_json[key]["answer"]
                
                # Generate embeddings for both answers
                answer_text_embedding = self.generate_embeddings(student_answer)
                answer_key_embedding = self.generate_embeddings(correct_answer)
                
                # Calculate similarity
                semantic_score = self.find_similarity(answer_text_embedding, answer_key_embedding)
                
                # Get the maximum possible marks for this question
                max_marks = answer_key_json[key]["Max Marks"]
                
                # If similarity is very low, assign 0 marks instead of rounding up
                score = math.ceil(max_marks * semantic_score) if semantic_score > 0.1 else 0
                
                # Store the score
                score_dict[key] = score

        return score_dict