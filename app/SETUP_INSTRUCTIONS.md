# Payroll Analytics — Setup Instructions (Auth + Dashboards)

## What's new
- Login / Logout with JWT + hashed passwords (bcrypt)
- Two roles: **Admin** and **Employee**
- Admin dashboard: Department Cost chart, Profit Statistics (income/expenses/payroll/net profit), Employee salaries, Add Employee, Performance chart (all employees)
- Employee dashboard: own salary + own performance chart only
- New backend models: `User`, `Transaction` (income/expense). `Employee` now has `department`, `position`, `performanceHistory`.

## 1. Backend setup

```bash
cd backend
npm install
```

Create a `.env` file (copy `.env.example`) and fill in:
```
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=replace_with_a_long_random_secret   # e.g. run: openssl rand -hex 32
PORT=5000
```

**Seed demo data (admin login + sample employees/transactions):**
```bash
npm run seed
```
This creates:
- Admin login → `admin@payroll.com` / `Admin@123`
- Employee login → `varun@company.com` / `Employee@123`
- 4 sample employees, 5 sample income/expense transactions

⚠️ **Change these passwords** after first login (or update the seed script) before this goes anywhere near real use.

**Run locally:**
```bash
npm start
```

## 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The API base URL is set in `frontend/src/api.js`:
```js
export const API_URL = 'https://payroll-analytics-dashboard.onrender.com';
```
Change this if your Render backend URL is different, or if testing locally (`http://localhost:5000`).

## 3. Deploying

**Backend (Render):**
- Push this updated `backend/` folder to your GitHub repo
- In Render dashboard → Environment → add `MONGO_URI` and `JWT_SECRET` (same values as your local `.env`)
- Render will redeploy automatically on push

**Frontend (Vercel):**
- Push the updated `frontend/` folder
- Vercel will redeploy automatically
- No new environment variables needed (API_URL is hardcoded in `api.js`) — but you could switch it to `import.meta.env.VITE_API_URL` and set it in Vercel's env vars if you prefer

**After deploying, run the seed script once** (either locally pointed at your production `MONGO_URI`, or via Render's shell) to create your admin account in production.

## 4. Creating more logins

Only an admin can create new logins. Once logged in as admin, you can call:
```
POST /api/auth/register
Authorization: Bearer <admin token>
{
  "name": "New Employee",
  "email": "new@company.com",
  "password": "somepassword",
  "role": "employee",
  "employeeId": "<the employee's _id from /api/employees>"
}
```
(There's no UI for this yet — it's an API call for now. Happy to build a "Manage Users" screen next if useful.)

## 5. Adding performance scores

Currently, performance history is added via:
```
PUT /api/employees/:id
Authorization: Bearer <admin token>
{ "performanceHistory": [{ "month": "2026-07", "score": 85 }, ...] }
```
This overwrites the array, so send the full updated list each time. A dedicated "Add performance entry" UI button would be a good next addition.
