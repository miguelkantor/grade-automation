#%% Imports
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

#%% Load environment variables from /Grade Automation/grade_automation.env
env_path = Path(__file__).parent / "grade_automation.env"
load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv("CANVAS_DOMAIN")
COURSE_ID = os.getenv("CANVAS_COURSE_ID")
API_TOKEN = os.getenv("CANVAS_API_TOKEN")

# Debug check for env variables
print("✅ Environment variable check:")
print("BASE_URL:", BASE_URL if BASE_URL else "❌ Missing")
print("COURSE_ID:", COURSE_ID if COURSE_ID else "❌ Missing")
print("API_TOKEN:", "✔︎ Loaded" if API_TOKEN else "❌ Missing")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

#%% Define Canvas API functions
def get_assignments():
    url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/assignments"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_students():
    url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/users?enrollment_type[]=student"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_submissions(assignment_id):
    url = f"{BASE_URL}/api/v1/courses/{COURSE_ID}/assignments/{assignment_id}/submissions"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

#%% Save raw data to /Grade Automation/raw_data
def save_raw(data, filename):
    raw_data_dir = Path(__file__).parent / "raw_data"
    raw_data_dir.mkdir(exist_ok=True)
    with open(raw_data_dir / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved: {filename}")

#%% Main logic
def main():
    print("\n📦 Fetching assignments...")
    assignments = get_assignments()
    save_raw(assignments, "assignments.json")

    print("\n📦 Fetching students...")
    students = get_students()
    save_raw(students, "students.json")

    print("\n📦 Fetching submissions per assignment...")
    for assignment in assignments:
        assignment_id = assignment['id']
        print(f"→ {assignment['name']} (ID: {assignment_id})")
        submissions = get_submissions(assignment_id)
        save_raw(submissions, f"submissions_{assignment_id}.json")

#%% Run
if __name__ == "__main__":
    main()
