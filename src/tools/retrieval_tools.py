from langchain_core.tools import tool


# Define tools for the retrieval agent
@tool
def search_jobs(query: str) -> str:
    """Search for job listings based on provided criteria such as role, location, experience level, etc."""
    # Mock response - in a real system, this would connect to job listing APIs
    if "software" in query.lower() and "california" in query.lower():
        return """
Found 120+ Software Engineering jobs in California:
1. Senior Software Engineer at TechCorp (San Francisco) - $150-180K - 5+ years experience required
2. Full Stack Developer at StartupX (Los Angeles) - $120-150K - 3+ years experience required  
3. Backend Engineer at DataSystems (San Diego) - $130-160K - 4+ years experience required
4. Junior Software Developer at InnovateTech (Silicon Valley) - $90-110K - 0-2 years experience
5. DevOps Engineer at CloudNine (Sacramento) - $140-170K - 3+ years experience required

Key requirements across these roles:
- Strong programming skills in languages like Python, Java, JavaScript
- Experience with cloud platforms (AWS, Azure, GCP)
- Computer Science or related degree (Bachelor's or Master's)
- Agile development experience
- Problem-solving skills and ability to work in teams
"""
    elif "ml" in query.lower() or "machine learning" in query.lower():
        return """
Found 85+ Machine Learning Engineer jobs:
1. Senior ML Engineer at AIScape (San Francisco) - $160-200K - 4+ years experience required
2. Machine Learning Engineer at DataMind (New York) - $150-180K - 3+ years experience required
3. ML Research Scientist at TechFrontier (Boston) - $170-210K - PhD preferred, 2+ years experience
4. Computer Vision Engineer at VisualAI (Seattle) - $140-180K - 3+ years experience required
5. NLP Engineer at LanguageTech (Remote) - $130-170K - 2+ years experience required

Key requirements across these roles:
- Strong Python programming and ML libraries (TensorFlow, PyTorch)
- Experience with deep learning and neural networks
- Statistics and mathematics background
- MS or PhD in Computer Science, Machine Learning, or related field
- Experience deploying ML models to production
"""
    elif "designer" in query.lower():
        return """
Found 90+ Designer jobs:
1. Senior UX Designer at CreativeMinds (San Francisco) - $120-150K - 5+ years experience required
2. Product Designer at DesignStudio (New York) - $100-130K - 3+ years experience required
3. UI Designer at TechVisuals (Seattle) - $90-120K - 2+ years experience required
4. Graphic Designer at BrandMakers (Los Angeles) - $70-100K - 2+ years experience required
5. UX/UI Designer at UserFirst (Remote) - $110-140K - 4+ years experience required

Key requirements across these roles:
- Portfolio demonstrating design skills
- Proficiency in design tools (Figma, Adobe Creative Suite)
- Understanding of user-centered design principles
- Experience working with product and engineering teams
- Degree in Design, HCI, or related field (often preferred but not always required)
"""
    else:
        return "Insufficient information provided for a targeted job search. Please provide more details about the job role, location, experience level, or other relevant criteria."
