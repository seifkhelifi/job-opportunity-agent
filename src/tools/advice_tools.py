from langchain_core.tools import tool


@tool
def get_resume_advice(
    job_type: str, skills: str = "", qualifications: str = "", challenges: str = ""
) -> str:
    """Get general resume advice for specific job types, considering skills, qualifications, and challenges."""
    # Mock response - in a real system, this might connect to a specialized career advice API
    if "software" in job_type.lower() or "developer" in job_type.lower():
        return """
For Software Engineering roles, consider these resume optimization strategies:

1. Technical Skills Section:
   - List programming languages, frameworks, and tools you're proficient in
   - Highlight cloud platforms experience (AWS, Azure, GCP)
   - Include relevant software development methodologies (Agile, Scrum)

2. Project Highlights:
   - Showcase 3-5 relevant projects with quantifiable results
   - Include GitHub links to personal projects or open-source contributions
   - Describe your role and specific technical challenges you overcame

3. Experience Format:
   - Use the STAR method (Situation, Task, Action, Result) to describe achievements
   - Quantify impact where possible (improved performance by X%, reduced costs by Y%)
   - Emphasize collaborative work and cross-functional experience

4. Education/Certifications:
   - Highlight relevant degrees (CS, Engineering, Math)
   - Include bootcamps or specialized training
   - List relevant certifications (AWS, Microsoft, Google)

5. Keywords:
   - Ensure your resume includes ATS-friendly keywords from job descriptions
   - Balance technical terms with soft skills (communication, teamwork)
"""
    elif "ml" in job_type.lower() or "machine learning" in job_type.lower():
        return """
For Machine Learning Engineering roles, consider these resume optimization strategies:

1. Technical ML Skills Section:
   - List ML libraries and frameworks (TensorFlow, PyTorch, scikit-learn)
   - Highlight experience with specific ML techniques (NLP, Computer Vision, etc.)
   - Include data processing tools and databases you've worked with

2. Project Highlights:
   - Describe ML models you've built with metrics of success
   - Explain datasets you've worked with and how you processed them
   - Highlight any research papers or publications

3. Experience Format:
   - Emphasize end-to-end ML pipeline experience
   - Highlight production deployment of ML models
   - Quantify model performance improvements

4. Education/Background:
   - Emphasize advanced degrees in relevant fields
   - Highlight statistics and mathematics background
   - Include relevant research experience

5. Common Gaps to Address:
   - Bridge between theoretical knowledge and practical implementation
   - Emphasize business impact of your ML work
   - Demonstrate both research and engineering capabilities
"""
    elif "designer" in job_type.lower():
        return """
For Design roles, consider these resume and portfolio optimization strategies:

1. Portfolio Focus:
   - Ensure your portfolio link is prominent on your resume
   - Include 5-8 diverse, high-quality projects
   - For each project, explain the problem, process, and outcome
   - Include both visual designs and user research/testing if applicable

2. Technical Skills:
   - List design tools you're proficient with (Figma, Sketch, Adobe XD)
   - Include prototyping and interaction tools
   - Mention research methodologies you're familiar with

3. Experience Format:
   - Highlight cross-functional collaboration with product and engineering
   - Explain your design thinking and decision-making process
   - Quantify impact of your designs when possible

4. Design Specialization:
   - Clearly indicate your specialization (UX, UI, Product, Graphic)
   - Show breadth of skills across the design spectrum
   - Highlight understanding of accessibility and inclusive design

5. Common Gaps to Address:
   - Balance aesthetic examples with problem-solving skills
   - Demonstrate business understanding and user-centered approach
   - Show iteration and improvement based on feedback
"""
    else:
        return "Please provide more specific information about the job type, skills, qualifications, or challenges you're facing to receive targeted resume advice."
