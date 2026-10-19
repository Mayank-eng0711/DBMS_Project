# Attendance Management System

Simple college DBMS project using HTML, CSS, JavaScript, Python Flask and MySQL. SQL is written manually in Python with `mysql-connector-python`; no ORM is used.

## Flat project files

- `app.py` — Flask backend and SQL queries
- `index.html` — web interface
- `style.css` — page styling
- `script.js` — browser interactions and API calls
- `database.sql` — MySQL tables and constraints
- `requirements.txt` — Python dependencies
- `vercel.json` — Vercel project configuration
- `Procfile` — start command for compatible Python hosts

## Run locally

1. Install Python 3.10+ and MySQL Server.
2. Open this folder in VS Code.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your MySQL credentials before running. Example for PowerShell:

   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_USER="root"
   $env:DB_PASSWORD="your_mysql_password"
   $env:DB_NAME="attendance_db"
   $env:DB_PORT="3306"
   ```

5. Run `python app.py` and open `http://127.0.0.1:5000`.

The local startup creates the database and tables; the MySQL user needs permission to create databases. Alternatively, run `database.sql` in MySQL Workbench first.

## GitHub

Upload the files in this folder directly to the root of your repository. Do not upload an extra parent folder around them.

```bash
git init
git add .
git commit -m "Add Attendance Management System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Vercel and MySQL

Vercel can host Flask apps, but deployment depends on the framework detection and Python runtime supported by your project settings. Set the Vercel Root Directory to the folder containing `app.py` and `requirements.txt`, then redeploy. If Vercel does not detect the Flask entry point, inspect Build Logs; the exact configuration can vary with Vercel's current Python runtime.

A deployed app cannot use `localhost` to reach MySQL on your laptop. Configure `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` to a separately hosted MySQL service. Create the schema on that server using `database.sql`. Keep passwords out of GitHub.
