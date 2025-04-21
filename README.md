# grade-automation

# Masterplan

## 1. Stakeholder Discovery & Requirements Gathering

### 🎯 Objective  
Understand the needs, workflows, and constraints of primary users: **LBS Faculty** and the **LBS Assessment Team**.

### 👥 Key Stakeholders  
- **Faculty**: Instructors who need to view and edit grades for their courses  
- **Assessment Team**: Admins overseeing grading policies, accuracy, and audits  
- **IT Team (optional)**: Involved for authentication (LBS SSO integration) and security policies

### 🗣️ Actions
- Conduct structured interviews or surveys with faculty and assessment staff  
- Document current workflows for exporting, modifying, and managing grades  
- Identify pain points with existing systems (e.g., Canvas UI, manual exports)  
- Capture user expectations around:  
  - Edit permissions and access control  
  - Grade visibility and auditability  
  - Collaboration needs  
  - Timelines (e.g., deadlines for grade finalization)

### ✅ Deliverables
- Stakeholder map with roles and responsibilities  
- User journey sketches (current vs. desired)  
- Initial feature requirements list  
- Draft policy for who can view/edit what (role-based matrix)

## 2. System Architecture Overview

### 🧱 High-Level Components
The system will be structured as a modular web application with the following core components:

- **Canvas API Integration**: Fetches assignments, submissions, and user data from Canvas
- **Centralized SQL Database**: Stores grade data, user roles, edit history, and course metadata
- **Backend API**: Handles data flow between the database, Canvas, and frontend
- **Frontend Interface**: Allows authenticated users to view, edit, and track grade information
- **Authentication Layer (LBS SSO)**: Secures access using LBS identity systems
- **Role-Based Access Control (RBAC)**: Enforces user permissions at row level

### 🔄 Data Flow Summary
1. Faculty/Assessment staff logs in via LBS SSO  
2. App fetches relevant Canvas data via API  
3. Grades and course data are stored and versioned in the central SQL database  
4. Authorized users can view or modify grades via the frontend  
5. Changes are committed to the SQL database, with proper audit tracking

### 🧩 Technologies (Tentative)
- **Backend**: Python (FastAPI or Flask)  
- **Frontend**: React or lightweight alternative  
- **Database**: PostgreSQL (centralized)  
- **Auth**: LBS SSO (OAuth2 or SAML)  
- **Infra**: Hosted on Heroku, Render, or LBS internal servers (TBD)

### ✅ Deliverables
- Initial system architecture diagram  
- Technology stack finalization  
- Auth strategy alignment with LBS IT  
- Canvas API usage plan

## 3. Authentication & Authorization

### 🔐 Authentication: LBS SSO Integration
All users will authenticate using **LBS Single Sign-On (SSO)** to ensure secure access and alignment with institutional policies.

- **Protocol**: OAuth2 or SAML (based on LBS infrastructure)
- **Identity provider**: London Business School
- **User profile data**: Extract user ID, name, email, and role (e.g., faculty, admin)

### 👮 Authorization: Role-Based Access Control (RBAC)

#### Roles & Permissions
| Role            | View Grades | Edit Grades | View All Courses | Edit All Courses |
|-----------------|-------------|-------------|------------------|------------------|
| Faculty         | ✅          | ✅ (their own) | ❌               | ❌               |
| Assessment Team | ✅          | ✅            | ✅               | ✅               |

#### Row-Level Access
- Faculty can only access data for courses they are explicitly assigned to
- Assessment Team has visibility across all courses and can override changes
- All data operations (view, edit, export) must enforce row-level authorization in backend queries

### 🛠️ Key Implementation Notes
- Use session tokens linked to LBS SSO auth
- Enforce access rules at the API/database level, not just frontend
- Consider middleware for permission checking on every endpoint

### ✅ Deliverables
- Auth flow diagram  
- RBAC ruleset and enforcement strategy  
- Access control checks implemented in backend routes  
- Working login/logout via LBS SSO

## 4. Canvas Data Integration

### 🎯 Objective  
Establish reliable data pipelines from Canvas to populate the SQL database with assignments, students, and grade data.

### 🔗 Canvas API Usage

#### Key Endpoints
- **Courses**: `/api/v1/courses/:course_id`
- **Assignments**: `/api/v1/courses/:course_id/assignments`
- **Submissions (Grades)**: `/api/v1/courses/:course_id/assignments/:assignment_id/submissions`
- **Users**: `/api/v1/courses/:course_id/users?enrollment_type[]=student`

#### Data Pulled
- Course metadata (name, term, code)
- Assignment details (name, ID, due date, points)
- Student list (name, email, user ID)
- Submission records (user ID, grade, submission state, timestamps)

### 🧠 Sync Strategy
- Scheduled sync (e.g., nightly or on-demand by admins)
- Store raw Canvas responses for traceability
- Normalize data into SQL tables:
  - `courses`
  - `assignments`
  - `students`
  - `submissions`
  - `sync_log`

### 🛡️ Considerations
- API rate limits (respect Canvas throttling policies)
- Pagination and data volume handling
- Error logging and retry mechanisms
- Canvas token security (stored securely, not exposed)

### ✅ Deliverables
- Working API integration with Canvas  
- Scripts for fetching and storing raw + normalized data  
- Scheduled or manual sync trigger system  
- Backup and audit strategy for raw Canvas data

## 5. Database Design

### 🏗️ Core Requirements
- Centralized SQL database accessible to backend API
- Support for multiple courses, terms, and programs
- Track both raw Canvas data and edited grades
- Enforce row-level access control based on user roles

### 📊 Core Tables

#### `courses`
| Field         | Type       | Notes                            |
|---------------|------------|----------------------------------|
| course_id     | TEXT (PK)  | Matches Canvas course ID         |
| name          | TEXT       | Course name                      |
| term          | TEXT       | Academic term                    |
| program       | TEXT       | MBA, MiM, etc.                   |
| created_at    | TIMESTAMP  | Auto-filled                      |

#### `assignments`
| Field            | Type       | Notes                            |
|------------------|------------|----------------------------------|
| assignment_id    | TEXT (PK)  | Matches Canvas assignment ID     |
| course_id        | TEXT (FK)  | Linked to `courses`              |
| name             | TEXT       | Assignment name                  |
| due_date         | TIMESTAMP  |                                  |
| total_points     | FLOAT      |                                  |

#### `students`
| Field       | Type       | Notes                            |
|-------------|------------|----------------------------------|
| student_id  | TEXT (PK)  | Matches Canvas user ID           |
| name        | TEXT       | Full name                        |
| email       | TEXT       | Unique                           |

#### `submissions`
| Field           | Type       | Notes                                |
|-----------------|------------|--------------------------------------|
| assignment_id   | TEXT (FK)  | Linked to `assignments`              |
| student_id      | TEXT (FK)  | Linked to `students`                 |
| grade           | TEXT       | Raw or updated grade                 |
| submitted_at    | TIMESTAMP  | Timestamp from Canvas                |
| edited_by       | TEXT       | User ID of person who edited         |
| edited_at       | TIMESTAMP  | Last edit time                       |
| source          | TEXT       | `canvas` or `manual`                 |

#### `users`
| Field       | Type       | Notes                                  |
|-------------|------------|----------------------------------------|
| user_id     | TEXT (PK)  | From LBS SSO                           |
| name        | TEXT       |                                        |
| email       | TEXT       |                                        |
| role        | TEXT       | `faculty`, `assessment_team`, etc.     |

#### `editing_flags`
| Field       | Type       | Notes                                  |
|-------------|------------|----------------------------------------|
| course_id   | TEXT       | Course currently being edited          |
| user_id     | TEXT       | Who is editing                         |
| timestamp   | TIMESTAMP  | When the editing session began         |

### ✅ Deliverables
- ERD (Entity-Relationship Diagram)
- SQL schema with constraints and foreign keys
- Initial migration scripts
- Database connection module for backend

## 5. Database Design (Revised)

### 🏧 Overview
The database schema is structured to support:
- Multiple users with defined roles (students, professors, TAs)
- Canvas-sourced and manually overwritten grade data
- Assignment- and course-level grade tracking
- Finalized grade calculations
- Support for programme-specific logic

### 📊 Core Tables

#### `Courses`
Stores course-level metadata.
```sql
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    term VARCHAR(50) NOT NULL
);
```

#### `Assignments`
Links assignments to courses with weight and type information.
```sql
CREATE TABLE Assignments (
    assignment_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES Courses(course_id),
    assignment_name VARCHAR(255) NOT NULL,
    max_points DECIMAL(10,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    type VARCHAR(50) NOT NULL -- (group, individual, peer)
);
```

#### `People`
Represents all users in the system (students, faculty, TAs).
```sql
CREATE TABLE People (
    person_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    programme_name VARCHAR(50),
    role VARCHAR(50) CHECK (role IN ('Student', 'Professor', 'TA')) NOT NULL
);
```

#### `CanvasAssignmentGrades`
Stores raw assignment-level grades fetched from Canvas.
```sql
CREATE TABLE CanvasAssignmentGrades (
    assignment_id INT REFERENCES Assignments(assignment_id),
    person_id INT REFERENCES People(person_id),
    raw_grade DECIMAL(10,2),
    PRIMARY KEY (assignment_id, person_id)
);
```

#### `GradeAssignmentOverwrites`
Tracks manual overrides to assignment grades, with full audit log.
```sql
CREATE TABLE GradeAssignmentOverwrites (
    overwrite_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES Assignments(assignment_id),
    person_id INT REFERENCES People(person_id),
    new_grade DECIMAL(10,2) NOT NULL,
    changed_by INT REFERENCES People(person_id),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `GradeCourseOverwrites`
Tracks manual course-level grade overrides (e.g., for final grades).
```sql
CREATE TABLE GradeCourseOverwrites (
    overwrite_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES Courses(course_id),
    person_id INT REFERENCES People(person_id),
    new_grade DECIMAL(10,2) NOT NULL,
    changed_by INT REFERENCES People(person_id),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `FinalizedAssignmentGrades`
Represents the finalized version of assignment grades.
```sql
CREATE TABLE FinalizedAssignmentGrades (
    assignment_id INT REFERENCES Assignments(assignment_id),
    person_id INT REFERENCES People(person_id),
    final_grade DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (assignment_id, person_id)
);
```

#### `FinalizedCourseGrades`
Represents the finalized course-level grades.
```sql
CREATE TABLE FinalizedCourseGrades (
    course_id INT REFERENCES Courses(course_id),
    person_id INT REFERENCES People(person_id),
    programme_name VARCHAR(50),
    weighted_score DECIMAL(10,2),
    letter_grade VARCHAR(2)
);
```

### ✅ Deliverables
- Normalized SQL schema ready for deployment
- Entity-Relationship Diagram (ERD)
- Initial migration scripts
- Secure connection to the backend with row-level permissions

## 6. Frontend Design

### 🎯 Objective
Provide a simple, intuitive interface for faculty and assessment staff to:
- View grades per course and assignment
- Edit grades (if authorized)
- Track edit history
- Monitor grading status (e.g. finalized or not)

### 🧩 Key Screens

#### 1. **Login Screen**
- LBS SSO authentication entry point

#### 2. **Dashboard**
- Lists all courses the user has access to
- Quick indicators for grading status per course

#### 3. **Course Detail Page**
- List of students and assignments in a table format
- Inline editing of grades (with “who is editing” indicator)
- Flags for overridden vs. raw grades
- Finalize grades button (if authorized)

#### 4. **Grade History Modal**
- Shows raw grade, all overrides, who made changes, and when
- Accessible via a “history” icon next to each editable grade

#### 5. **Admin Panel (Assessment Team Only)**
- Manage user roles and course access
- Trigger Canvas sync manually
- Export final grades

### 🛡️ Permissions in UI
- Only show edit controls if user has permission
- Disable editing if another user is actively editing
- Hide courses/assignments outside of user’s access scope

### 🛠️ Technology Stack (Suggested)
- **Framework**: React or Svelte
- **State Management**: React Context or Zustand
- **Styling**: Tailwind CSS
- **Auth Handling**: Use session-based tokens from SSO

### ✅ Deliverables
- Interactive wireframes for all screens
- Frontend component tree
- Role-based interface behavior spec
- Editable table with permission-aware logic

## 7. Editing & Versioning Logic

### 🎯 Objective
Enable users to safely edit grades while preserving raw Canvas data, tracking changes, and avoiding conflicts during simultaneous edits.

### ✏️ Editing Model

#### Phase 1: Basic Sequential Editing
- Only one user can edit a course at a time
- A flag in the database (`editing_flags`) stores:
  - `course_id`
  - `user_id` of current editor
  - `timestamp` of edit session start
- Other users see the course as "locked for editing"

#### Phase 2 (Future): Real-Time Collaboration
- WebSocket-based live updates across users
- Collaborative editing with granular locks per assignment or student
- Live presence indicators

### 🧾 Grade Versioning

#### Canvas Data
- Raw grades pulled from Canvas stored in `CanvasAssignmentGrades`
- Never overwritten — serves as the baseline

#### Manual Edits
- Stored in `GradeAssignmentOverwrites` and `GradeCourseOverwrites`
- Track:
  - Editor (`changed_by`)
  - Timestamp
  - New value
  - Overwrite reason (optional in v2)

#### Finalization
- Once finalized, grades are written to:
  - `FinalizedAssignmentGrades`
  - `FinalizedCourseGrades`
- After finalization, editing is disabled unless explicitly reopened by admin

### 🔍 Edit History Access
- Full grade history shown in frontend via modal or tooltip
- Allows comparison of raw vs. overwritten vs. finalized values

### ✅ Deliverables
- Edit-locking mechanism in backend
- Overwrite audit log tables
- Frontend logic for locking, saving, and reverting edits
- UI for finalized grades and their visibility

## 8. Team Roles & Timeline Planning

### 🧑‍🤝‍🧑 Team Structure
The project will be executed by a 5-person team, with members assigned to overlapping but distinct workstreams.

#### Suggested Role Breakdown
| Area                   | Responsibilities                                            | Owner(s)         |
|------------------------|-------------------------------------------------------------|------------------|
| Project Management     | Stakeholder coordination, timeline tracking, task planning  | TBD              |
| Backend/API            | Canvas integration, DB setup, auth logic, edit/versioning   | TBD              |
| Frontend Development   | UI for grade editing, locking states, data visualizations   | TBD              |
| Database Design        | Schema design, migrations, SQL integration                  | TBD              |
| DevOps/Deployment      | GitHub repo, CI/CD setup, hosting (Heroku/Render/etc.)      | TBD              |

### 📅 Tentative Timeline

#### Week 1–2: Discovery & Setup
- Stakeholder interviews
- Auth scope confirmation with LBS IT
- Repo setup, base schema finalized

#### Week 3–4: Backend Foundations
- Canvas data pipeline operational
- Initial DB schema deployed
- Auth and access control scaffolding

#### Week 5–6: Frontend Buildout (v1)
- Course view + grade table
- Basic editing and save functionality
- Frontend-backend integration

#### Week 7: Testing & Polish
- Bug fixing, grade overwrite history
- Grade finalization & lock states
- User feedback loop (faculty/assessment team)

#### Week 8: Launch & Handover
- Final deployment
- Documentation + user manual
- Handoff meeting and post-launch support window

### ✅ Deliverables
- Defined owners for each project area  
- Timeline with weekly goals/milestones  
- Agile board with tasks broken by stream  
- Regular sync schedule (e.g., twice a week)
