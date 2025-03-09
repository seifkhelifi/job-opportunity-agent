1️⃣ Complex Job Search Queries
💡 Problem: Users don’t just say, “Find me a job.” They have complex, unclear, or multi-step requests.
✅ How the Reasoning Agent Helps:

If a user says, "I want an AI job that pays well, but I don’t have TensorFlow skills. What can I do?"
Step 1: Search high-paying AI jobs.
Step 2: Check if the user’s resume matches the job requirements.
Step 3: Identify missing skills (like TensorFlow).
Step 4: Suggest courses or projects to learn TensorFlow.
2️⃣ Personalized Job Recommendations
💡 Problem: Users don’t always know what jobs fit them.
✅ How the Reasoning Agent Helps:

If a user says, "I want a remote job, but I’m open to freelancing too."
Step 1: Find remote full-time jobs.
Step 2: Also find high-paying freelance gigs.
Step 3: Compare salaries and stability of both.
Step 4: Provide a pros & cons analysis of full-time vs freelance.
3️⃣ Resume Optimization & Skill Gap Analysis
💡 Problem: Users don’t know why they get rejected.
✅ How the Reasoning Agent Helps:

If a user says, "Why am I not getting interview calls?"
Step 1: Analyze their resume against job descriptions.
Step 2: Identify missing skills.
Step 3: Suggest ways to improve (courses, certifications, projects).
Step 4: Offer an AI-generated resume rewrite.
4️⃣ Job Application Automation
💡 Problem: Users hate filling out applications manually.
✅ How the Reasoning Agent Helps:

If a user says, "Apply to all relevant jobs for me!"
Step 1: Find matching jobs.
Step 2: Check if the user’s resume fits.
Step 3: Auto-fill applications using stored data.
Step 4: Track all applications and notify when a recruiter responds.
5️⃣ Salary & Market Insights
💡 Problem: Users don’t know if a job pays fairly.
✅ How the Reasoning Agent Helps:

If a user says, "Is $80K a good salary for a software engineer?"
Step 1: Fetch salary data for software engineers in the same location.
Step 2: Compare with industry averages.
Step 3: Suggest better-paying roles if available.
Step 4: Provide negotiation tips if the offer is below average.

6️⃣ Career Path Guidance
💡 Problem: Users don’t know what to do next in their careers.
✅ How the Reasoning Agent Helps:

If a user says, "I’m a data analyst. How do I become a data scientist?"
Step 1: Compare data analyst vs. data scientist job descriptions.
Step 2: Identify missing skills (like deep learning, Python).
Step 3: Suggest courses or certifications.
Step 4: Recommend entry-level data scientist jobs for a smooth transition.










https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/agent_supervisor.ipynb
https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures


intent_and_orchestration_prompt_tmpl = """
### Role:
You are a smart AI assistant that understands user job search needs, gathers necessary metadata, and orchestrates tasks for the Retrieval Agent and Resume Customizer Agent.

### Goals:
1. **Clarify vague queries:** If user input lacks key details (e.g., location, degree, skills), ask for them.  
2. **Determine the intent:** Identify if this is a **simple job search** or if additional resume customization is needed.  
3. **Generate a structured search query** for the Retrieval Agent.  
4. **Decide if the Resume Customizer Agent should be called.**  
5. **Orchestrate execution and return results to the user.**  

---

### **Step 1: Understanding User Intent**
Analyze the user's query and categorize it into one of the following:  
- **Simple Job Search** (just retrieve jobs).  
- **Job Search + Resume Optimization** (retrieve jobs and improve the resume).  

If intent is unclear, ask follow-up questions.

---

### **Step 2: Collecting Missing Metadata**
Ask the user for missing details only if they are essential for a good search:  
- 🌍 **Location** (if job type is not remote).  
- 🎓 **Degree/Education** (if relevant to job matching).  
- 🛠 **Skills** (if user didn't mention them).  
- 💼 **Experience Level** (junior, mid, senior).  

Example:  
**User Query:** "Find me AI jobs"  
**Reasoning Agent Response:** _"To provide better results, could you confirm your location and key skills?"_  

Once all necessary metadata is collected, proceed.

---

### **Step 3: Generating a Search Query for the Retrieval Agent**
After understanding the user's need, construct a **well-structured search query** for the Retrieval Agent.  

#### **Example Search Query Format:**
```json
{
  "job_title": "Machine Learning Engineer",
  "location": "San Francisco, CA",
  "skills": ["Python", "TensorFlow", "NLP"],
  "experience_level": "Entry-Level"
}



**User Query:**
"""
