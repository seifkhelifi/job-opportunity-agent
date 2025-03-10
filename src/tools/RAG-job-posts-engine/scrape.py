import csv
from jobspy import scrape_jobs

# Define job specialties to cover diverse tech roles
tech_specialties = [
    "software engineer",
    "data scientist",
    "cybersecurity analyst",
    "AI engineer",
    "cloud engineer",
    "devops engineer",
    "UI/UX designer",
    "full stack developer",
    "mobile app developer",
    "machine learning engineer",
]

# Define target locations
locations = {
    "USA": "San Francisco, CA",
    "UK": "London, England",
    "France": "Paris, France",
}

# Collect jobs
all_jobs = []
for country, location in locations.items():
    for specialty in tech_specialties:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor"],
            search_term=specialty,
            location=location,
            results_wanted=15,  # Limit to 15 per specialty per location
            hours_old=72,  # Jobs posted in the last 3 days
            country_indeed=country,
            linkedin_fetch_description=True,  # Fetch job descriptions
        )
        all_jobs.extend(jobs.to_dict(orient="records"))

# Save to CSV
fieldnames = all_jobs[0].keys() if all_jobs else []
if all_jobs:
    with open("tech_jobs_dataset.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\"
        )
        writer.writeheader()
        writer.writerows(all_jobs)
    print(f"Saved {len(all_jobs)} job postings to tech_jobs_dataset.csv")
else:
    print("No job postings found.")

