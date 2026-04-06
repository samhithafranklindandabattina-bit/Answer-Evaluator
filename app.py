import streamlit as st
from main import *
import pandas as pd
import warnings
import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# Custom CSS for styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-color: #f5f5f5;
}

h1, h2, h3 {
    text-align: center !important;
    color: #6a0dad !important;
}

.stButton>button {
    background-color: #6a0dad;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #5a0c9d;
    color: white;
}

.stExpander {
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.stDataFrame {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.css-1aumxhk {
    background-color: #6a0dad;
    color: white;
}

.instruction-box {
    border-left: 4px solid #6a0dad;
    padding: 1rem;
    margin-bottom: 1.5rem;
    border-radius: 0 8px 8px 0;
}
</style>
""", unsafe_allow_html=True)

# Background Image
background_image_url = "https://png.pngtree.com/thumb_back/fh260/background/20240104/pngtree-mystic-blackberry-a-textured-design-on-an-abstract-dark-purple-background-image_13879614.png"
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url({background_image_url});
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stAppViewContainer"]::before {{
content: "";
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 100%;
background-color: rgba(0, 0, 0, 0.7);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Instruction Sections
def quick_guide():
    with st.expander("📘 QUICK START GUIDE - Click to Expand", expanded=False):
        st.markdown("""
        <div class="instruction-box">
        <h4>🚀 Get Started in 4 Steps</h4>
        
        1. <strong>Prepare Answer Key</strong>  
           - Create JSON file with model answers  
           ```json
           {"Q1": {"Answer": "Sample answer", "Max Marks": 5}}
           ```
        
        2. <strong>Format Answer Sheets</strong>  
           - Each PDF must contain:  
           ```plaintext
           Question 1:  
           Answer: Student's response...
           ```
        
        3. <strong>Upload & Grade</strong>  
           - Add student details  
           - Upload their answer PDFs  
           - Click "Grade All Answers"
           
        4. <strong>Sample Files</strong>  
           - Download test answer sheets and templates:  
           [GitHub Repository](https://github.com/Akshint0407/Automated-Answer-Checker/tree/main/Test) 🔗  
        </div>
        """, unsafe_allow_html=True)
quick_guide()

def full_instructions():
    st.markdown("""<a name="full-guide"></a>""", unsafe_allow_html=True)
    with st.expander("📚 COMPLETE USER MANUAL", expanded=False):
        st.markdown("""
        ## 📝 Answer Key Preparation
        **File Format:** JSON  
        **Required Structure:**
        ```json
        {
          "Q1": {
            "Answer": "The capital of France is Paris",
            "Max Marks": 5
          },
          "Q2": {
            "Answer": "2πr",
            "Max Marks": 3
          }
        }
        ```
        
        ## 🖨️ Answer Sheet Requirements
        - **Scanning:** 300dpi or higher resolution
        - **Formatting:**
        ```plaintext
        Question 3:
        Answer: The mitochondria is the powerhouse...
        ```
        - **File Type:** PDF (one file per student)
        
        ## 🧑‍🎓 Student Data Entry
        1. Enter total number of students
        2. For each student:
           - Full name
           - Roll number
           - Upload formatted answer PDF
        
        ## 🔍 Understanding Results
        - **Score Calculation:** AI compares answers using semantic similarity
        - **Color Coding:**
          - >80% match: Green highlight
          - 40-80% match: Yellow highlight
          - <40% match: Red highlight
        - **Export Options:** CSV download available
        """)

# Main App Title and Description
st.title("📝 Automated Answer Checker")
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
This app allows teachers to upload an answer key and student answer sheets for automated grading of multiple students.
</div>
""", unsafe_allow_html=True)

# Upload Answer Key
st.header("📝 Upload Answer Key")
answer_key_file = st.file_uploader("Upload Answer Key (JSON format)", type="json", key="answer_key")

if answer_key_file:
    st.success("Answer key uploaded successfully!")

    # Student Management
    st.header("👥 Student Details")
    num_students = st.number_input("Number of Students", min_value=1, max_value=50, value=1, key="num_students")
    if st.button("Continue"):
        st.session_state.students = [{} for _ in range(num_students)]
        st.session_state.stage = "student_details"

# Student Answer Submission
if st.session_state.get("stage") == "student_details":
    st.header("📤 Student Answer Submission")
    for i in range(len(st.session_state.students)):
        with st.expander(f"Student {i + 1}", expanded=False):
            name = st.text_input("Full Name", key=f"name_{i}")
            roll_no = st.text_input("Roll Number", key=f"roll_{i}")
            pdf_file = st.file_uploader(
                "Upload Answer PDF",
                type=["pdf"],
                key=f"pdf_{i}",
                accept_multiple_files=False  # Single PDF per student
            )
            if name and roll_no and pdf_file:
                st.success("Answersheet PDF uploaded successfully!")
                st.session_state.students[i] = {
                    "name": name,
                    "roll_no": roll_no,
                    "pdf_file": pdf_file
                }
    
    if st.button("Grade All Answers"):
        st.session_state.stage = "results"

# Results Display
if st.session_state.get("stage") == "results":
    st.header("📊 Grading Results")
    progress_text = st.empty()
    summary_data = []
    detailed_data = []
    api_key = "K85286034988957"  # Replace with your actual API key
    
    progress_bar = st.progress(0)
    total_students = len([s for s in st.session_state.students if "pdf_file" in s and s["pdf_file"]])
    processed_count = 0

    with st.spinner("Extracting and grading answers..."):
        for i, student in enumerate(st.session_state.students):
            if "pdf_file" not in student or not student["pdf_file"]:
                continue
            progress_text.text(f"Processing {student.get('name', 'Student ' + str(i+1))} ({i+1} of {total_students})...")
            try:
                print("here")
                scores = main_st(student["pdf_file"], answer_key_file, api_key)
                total = sum(scores.values())
                max_marks = len(scores) * 10
                percentage = (total / max_marks) * 100 if max_marks > 0 else 0
                print("here")
                student_record = {
                    "Roll No": student.get("roll_no", "N/A"),
                    "Name": student.get("name", "N/A"),
                    **scores,
                    "Total": total,
                    "Percentage": percentage,
                    "max_marks" : max_marks
                }
                summary_data.append({
                    "Roll No": student_record["Roll No"],
                    "Name": student_record["Name"],
                    "Percentage": percentage  # Float
                })
                detailed_data.append(student_record)
                
                processed_count += 1
                progress_bar.progress(int((processed_count / total_students) * 100) if total_students > 0 else 100)
            
            except Exception as e:
                st.error(f"Error processing {student.get('name', 'Unknown')}: {str(e)}")
    
    progress_text.text("Grading complete!")
    progress_bar.progress(100)
    
    if summary_data:
        st.subheader("Overall Results")
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(
            summary_df.style.format({"Percentage": "{:.2f}%"}),
            use_container_width=True
        )
        
        with st.expander("View Detailed Results", expanded=False):
            detailed_df = pd.DataFrame(detailed_data)
            # Dynamically order columns
            base_columns = ["Roll No", "Name"]
            question_columns = [col for col in detailed_df.columns if col.startswith('a')]
            other_columns = ["Total", "Percentage"]
            existing_columns = [col for col in base_columns + question_columns + other_columns if col in detailed_df.columns]
            
            st.dataframe(
                detailed_df[existing_columns].style.format({"Percentage": "{:.2f}%"}),
                use_container_width=True
            )
            # Download button for detailed results
            csv = detailed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Detailed Results",
                data=csv,
                file_name="grading_results.csv",
                mime="text/csv"
            )
    else:
        st.warning("⚠️ No student data available for display")
    
    def reset_app():
        # Clear all session state
        st.session_state.clear()
        # Clear cache
        st.cache_data.clear()
        # Rerun from beginning
        st.rerun()

    # Then modify your button:
    if st.button("Start New Grading Session"):
        reset_app()

full_instructions()

# Add a footer
st.markdown("---")
st.markdown("Built with ❤️ by 2nd year AI & DS  | Powered by Streamlit")
