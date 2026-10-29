# PublicSpace360 - Smart City Public Space Usage & Digital Mapping Platform

> **Project Topic:** Public Space Usage and Digital Mapping  
> **Tagline:** *"Mapping Public Spaces. Understanding People. Improving Communities."*  
> **Project Type:** College Community Engagement Project (CEP) / Smart City Civic Tech  
> **Stack:** Python 3, Flask, MySQL (`mysql-connector-python` / `PyMySQL`), Bootstrap 5.3, Leaflet.js, OpenStreetMap, Chart.js, Font Awesome  

---

## 📌 1. Project Overview & CEP Purpose

**PublicSpace360** is a full-featured civic GIS and citizen feedback web platform developed as an undergraduate Community Engagement Project (CEP). Rapid urbanization often leaves public parks, playgrounds, gardens, promenades, and outdoor fitness zones unevenly distributed, under-maintained, or inaccessible to diverse demographic cohorts.

PublicSpace360 bridges the gap between citizens, students, and municipal town planners by:
1. **Digitally Mapping Urban Public Spaces:** Visualizing civic amenities on an interactive OpenStreetMap engine powered by Leaflet.js with category-specific spatial markers.
2. **Measuring Citizen Usage:** Collecting targeted demographic data on visit frequency, transportation modes, primary purpose, and age cohorts.
3. **Evaluating Facility Quality:** Rating civic infrastructure across 6 dimensions: *Safety*, *Cleanliness*, *Lighting*, *Seating*, *Drinking Water*, and *Universal Accessibility*.
4. **Crowdsourcing Civic Maintenance:** Empowering residents to report broken streetlamps, damaged playground equipment, hygiene failures, or safety risks with photo evidence.
5. **Informing Municipal Interventions:** Synthesizing survey data into real-time Chart.js telemetry for evidence-based urban governance.

---

## 🏛️ 2. Key Features

### For Citizens & Community Members:
- **Scenic Smart City Home Experience:** Visually rich hero section with dark navy navbar (`#06283D`), green brand accents (`#21F58B`), interactive floating map preview card, real-time animated statistics strip, and category showcase.
- **Interactive Fullscreen GIS Map (`/map`):** Live map with category filters (Parks, Playgrounds, Promenades, Gardens, Open Gyms), instant keyword search, and rich popups with opening times, visitor estimates, and facility checklists.
- **Public Spaces Directory (`/spaces`):** Catalog with sorting, category filtering, facility tags, and individual profiles (`/spaces/<id>`).
- **12-Question CEP Usage Survey (`/survey`):** Structured questionnaire measuring community engagement, safety perceptions, and improvement priorities.
- **Dynamic Analytics Dashboard (`/results`):** Live Chart.js telemetry charts generated from MySQL database records (pie charts, bar charts, doughnut charts, and response trends).
- **Civic Problem Reporting (`/report`):** Photo-enabled issue filing with status lifecycle tracking (*Reported* &rarr; *Under Review* &rarr; *In Progress* &rarr; *Resolved*).
- **Citizen Dashboard (`/dashboard`):** Personal survey history, report tickets, and citizen profile.

### For Municipal Administrators & CEP Researchers:
- **Dedicated Admin Portal (`/admin/login`):** Role-gated authentication with Werkzeug password hashing.
- **Smart City Operations Control Center (`/admin/dashboard`):**
  - **Public Space Inventory Management:** Full CRUD (Add space, Edit coordinates/facilities/hours, Delete space).
  - **Survey Responses Data Grid:** Search, filter, and 1-click **Export to CSV** for statistical analysis in Excel, SPSS, or Python Pandas.
  - **Civic Report Resolution Engine:** Interactive dropdown status updates with priority badges (*Low*, *Medium*, *High*, *Critical*).
  - **User & Community Management:** View citizen demographic breakdown.

---

## 💻 3. Technology Stack

- **Frontend:**
  - HTML5, CSS3, JavaScript ES6
  - Bootstrap 5.3 (Responsive Grid, Modals, Toasts)
  - Google Fonts (`Poppins` & `Inter`)
  - Font Awesome 6.6 Icons
  - **GIS & Mapping:** Leaflet.js (v1.9.4) + OpenStreetMap (No Google API key required)
  - **Data Visualization:** Chart.js (v4.4.1)
- **Backend:**
  - Python 3.9+
  - Flask (Modular routing, sessions, templates)
  - Werkzeug (Secure password hashing via `generate_password_hash` and `check_password_hash`, `secure_filename`)
- **Database:**
  - MySQL 8.0+
  - Connectors: `mysql-connector-python` and `PyMySQL`
  - Dual-mode connection with automatic reliable SQLite fallback (`database/publicspace360.db`) ensuring immediate execution even if a local MySQL daemon is not running during demonstration.

---

## 📂 4. Project Folder Structure

```
PublicSpace360/
│
├── app.py                          # Main Flask server with 35+ routes and REST APIs
├── config.py                       # Application configuration & database credentials
├── db.py                           # Dual-mode database layer (MySQL + SQLite fallback)
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment variable template
├── README.md                       # Comprehensive project documentation
├── test_app.py                     # Automated end-to-end test suite
│
├── database/
│   ├── publicspace360.sql          # Complete MySQL schema & realistic seed dataset
│   └── publicspace360.db           # Pre-seeded SQLite database for zero-friction launch
│
├── templates/
│   ├── base.html                   # Master layout (Dark navy navbar, toast container, footer)
│   ├── index.html                  # Homepage matching Smart City reference design
│   ├── login.html                  # Split-screen user login
│   ├── register.html               # Citizen registration with age groups & validation
│   ├── dashboard.html              # Citizen activity dashboard
│   ├── map.html                    # Fullscreen interactive Leaflet GIS map
│   ├── spaces.html                 # Public spaces directory with live search & filters
│   ├── space-details.html          # Individual space profile, ratings, and feedback form
│   ├── survey.html                 # 12-question CEP questionnaire
│   ├── results.html                # Dynamic Chart.js analytics visualizations
│   ├── report.html                 # Problem reporting with photo file upload
│   ├── about.html                  # Academic CEP project background & UN SDGs
│   ├── contact.html                # Contact form & municipal office details
│   ├── admin-login.html            # Dedicated secure admin access portal
│   └── admin-dashboard.html        # Smart City Operations control center
│
├── static/
│   ├── css/
│   │   ├── style.css               # Core styling, glassmorphism, brand color system
│   │   ├── responsive.css          # Breakpoints (1440px+, 992px, 768px, <768px)
│   │   └── admin.css               # Dark Smart City admin portal aesthetics
│   │
│   ├── js/
│   │   ├── main.js                 # Global interactions, toast alerts, animated counters
│   │   ├── map.js                  # Leaflet map markers, clustering, and filters
│   │   ├── survey.js               # Survey form validation & scale interactions
│   │   ├── results.js              # Dynamic Chart.js telemetry charts
│   │   ├── dashboard.js            # User dashboard filters and actions
│   │   └── admin.js                # Space CRUD, issue status, and CSV export
│   │
│   └── images/
│       ├── hero.jpg                # Scenic park background with walking track
│       ├── park.jpg                # Urban green park
│       ├── playground.jpg          # Adventure children playground
│       ├── promenade.jpg           # Waterfront coastal promenade
│       ├── garden.jpg              # Botanical rose garden
│       └── open-gym.jpg            # Community fitness equipment
│
└── uploads/
    └── reports/                    # Secure photo storage for citizen issue reports
```

---

## ⚙️ 5. Installation & Setup

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed
- (Optional for MySQL mode) MySQL Server or XAMPP / WampServer

### Step 1: Clone or Navigate to Project
```bash
cd C:\Users\priyanka\.gemini\antigravity\scratch\PublicSpace360
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database (Two Options)

#### Option A: Instant Zero-Config SQLite Mode (Default)
The application includes a pre-seeded `database/publicspace360.db` file. If MySQL is not running or credentials are not configured, the app automatically runs in SQLite mode with 100% of features working out-of-the-box!

#### Option B: Native MySQL Mode
1. Start your local MySQL server (via MySQL Workbench, XAMPP, or Windows Service).
2. Create a `.env` file by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your MySQL credentials:
   ```env
   SECRET_KEY=publicspace360_secret_key_2026
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=publicspace360
   MYSQL_PORT=3306
   ```
4. Import the schema and seed data into MySQL:
   ```bash
   mysql -u root -p < database/publicspace360.sql
   ```
   *(Or import `database/publicspace360.sql` using phpMyAdmin's "Import" tab)*.

---

## 🚀 6. Running the Application

Launch the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔐 7. Demo Credentials

### Administrator Portal (`/admin/login`):
- **Email:** `admin@publicspace360.org`
- **Password:** `admin123`
- *Secondary Admin:* `planner@citygov.org` / `admin123`

### Citizen Portal (`/login`):
- **Email:** `user@example.com`
- **Password:** `user123`
- *(Or click **Register** to create a new citizen account with custom age group and demographic parameters)*.

---

## 📊 8. REST API Documentation

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/register` | Register citizen with demographic profile | No |
| `POST` | `/api/login` | Citizen session authentication | No |
| `POST` | `/api/logout` | Terminate citizen session | No |
| `POST` | `/api/admin/login` | Administrator session authentication | No |
| `POST` | `/api/admin/logout` | Terminate admin session | Yes (Admin) |
| `GET` | `/api/statistics` | Dynamic metric counters (spaces, responses, categories) | No |
| `GET` | `/api/spaces` | Public space list with category & search query filters | No |
| `GET` | `/api/spaces/<id>` | Single public space detailed profile | No |
| `POST` | `/api/spaces` | Create new public space | Yes (Admin) |
| `PUT` | `/api/spaces/<id>` | Update public space details | Yes (Admin) |
| `DELETE` | `/api/spaces/<id>` | Delete public space | Yes (Admin) |
| `GET` | `/api/surveys` | Fetch survey responses (filter by space) | No |
| `POST` | `/api/surveys` | Submit 12-question CEP questionnaire | Yes (User) |
| `DELETE` | `/api/surveys/<id>` | Delete survey response | Yes (Admin) |
| `GET` | `/api/reports` | Retrieve citizen problem reports | No |
| `POST` | `/api/reports` | Submit civic problem with photo upload | Yes (User) |
| `PUT` | `/api/reports/<id>` | Update report status (*In Progress*, *Resolved*) | Yes (Admin) |
| `POST` | `/api/feedback` | Submit space review & rating | Yes (User) |
| `GET` | `/api/feedback/<id>` | Fetch reviews for a specific public space | No |
| `GET` | `/api/analytics` | Aggregated telemetry data for Chart.js | No |
| `GET` | `/api/users` | List registered community members | Yes (Admin) |
| `DELETE` | `/api/users/<id>` | Remove user account | Yes (Admin) |
| `POST` | `/api/contact` | Submit contact / collaboration message | No |

---

## 🎓 9. College CEP Presentation & Viva Talking Points

When demonstrating this project for your College Community Engagement Project review or viva examination, highlight the following technical and social engineering aspects:

1. **Alignment with UN Sustainable Development Goal 11 (SDG 11):**  
   Target 11.7 calls for providing *“universal access to safe, inclusive and accessible, green and public spaces, in particular for women and children, older persons and persons with disabilities.”* PublicSpace360 directly measures accessibility, safety, and gender inclusion.
2. **Dual-Mode Architectural Resilience:**  
   Explain that the database layer (`db.py`) dynamically detects MySQL and falls back seamlessly to SQLite, guaranteeing 100% demonstration reliability during examinations without relying on local daemon state.
3. **Data Integrity & Security:**  
   Show how passwords use modern key derivation (Werkzeug scrypt/pbkdf2), queries use parameterized SQL inputs (`%s`) preventing SQL injection, and file uploads are secured with `secure_filename` and MIME extension whitelisting.
4. **Client-Side GIS vs Heavy Map APIs:**  
   Explain why Leaflet.js + OpenStreetMap was chosen over Google Maps: lightweight footprint, complete tile privacy, no API quota billing, and custom SVG colored marker pins.
5. **Real-Time Data Visualizations:**  
   Demonstrate how `/api/analytics` dynamically groups survey data by age cohort and space category in SQL, returning JSON that feeds into 5 distinct Chart.js visualizations on `/results`.

---

## 📄 License & Attribution
Developed for College Community Engagement Project (CEP) Academic Presentation. Open-source under the MIT License.
