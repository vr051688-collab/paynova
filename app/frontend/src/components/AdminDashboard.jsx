import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend
} from 'recharts';
import { apiFetch } from '../api';

const COLORS = ['#f09433', '#dc2743', '#bc1888', '#8e44ad', '#2980b9'];

export default function AdminDashboard() {
  const [employees, setEmployees] = useState([]);
  const [users, setUsers] = useState([]);
  const [deptCost, setDeptCost] = useState([]);
  const [profitStats, setProfitStats] = useState(null);
  const [performance, setPerformance] = useState([]);
  const [form, setForm] = useState({ name: '', email: '', salary: '', department: '', position: '' });
  const [loading, setLoading] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [emp, dc, ps, perf, usr] = await Promise.all([
        apiFetch('/api/employees'),
        apiFetch('/api/dashboard/department-cost'),
        apiFetch('/api/dashboard/profit-stats'),
        apiFetch('/api/dashboard/performance'),
        apiFetch('/api/auth/users')
      ]);
      setEmployees(emp || []);
      setDeptCost(dc || []);
      setProfitStats(ps);
      setPerformance(perf || []);
      setUsers(usr || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, []);

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      await apiFetch('/api/employees', {
        method: 'POST',
        body: JSON.stringify({ ...form, salary: Number(form.salary) })
      });
      setForm({ name: '', email: '', salary: '', department: '', position: '' });
      loadAll();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleLinkEmployee = async (userId, employeeId) => {
    try {
      await apiFetch(`/api/auth/link-employee/${userId}`, {
        method: 'PUT',
        body: JSON.stringify({ employeeId: employeeId || null })
      });
      loadAll();
    } catch (err) {
      alert(err.message);
    }
  };

  // Build performance chart data: one line per employee, x = month
  const perfChartData = (() => {
    const months = new Set();
    performance.forEach(p => p.performanceHistory?.forEach(h => months.add(h.month)));
    const sortedMonths = Array.from(months).sort();
    return sortedMonths.map(month => {
      const row = { month };
      performance.forEach(p => {
        const entry = p.performanceHistory?.find(h => h.month === month);
        if (entry) row[p.name] = entry.score;
      });
      return row;
    });
  })();

  if (loading) return <p>Loading dashboard...</p>;

  return (
    <div className="dashboard">
      {/* Profit Statistics */}
      {profitStats && (
        <section className="stats-grid">
          <div className="card stat-card">
            <p className="stat-label">Total Income</p>
            <p className="stat-value income">₹{profitStats.totalIncome.toLocaleString()}</p>
          </div>
          <div className="card stat-card">
            <p className="stat-label">Total Expenses</p>
            <p className="stat-value expense">₹{profitStats.totalExpenses.toLocaleString()}</p>
          </div>
          <div className="card stat-card">
            <p className="stat-label">Total Payroll</p>
            <p className="stat-value payroll">₹{profitStats.totalPayroll.toLocaleString()}</p>
          </div>
          <div className="card stat-card">
            <p className="stat-label">Net Profit</p>
            <p className={`stat-value ${profitStats.netProfit >= 0 ? 'income' : 'expense'}`}>
              ₹{profitStats.netProfit.toLocaleString()}
            </p>
          </div>
        </section>
      )}

      {/* Department Cost Chart */}
      <section className="card chart-card">
        <h2>Department Cost</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={deptCost}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="department" />
            <YAxis />
            <Tooltip formatter={(v) => `₹${v.toLocaleString()}`} />
            <Bar dataKey="totalCost" fill="#dc2743" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Performance Chart */}
      <section className="card chart-card">
        <h2>Employee Performance</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={perfChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            {performance.map((p, i) => (
              <Line key={p._id} type="monotone" dataKey={p.name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Add Employee */}
      <form className="card form-card" onSubmit={handleAddEmployee}>
        <h2>Add Employee</h2>
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input placeholder="Salary" type="number" value={form.salary} onChange={(e) => setForm({ ...form, salary: e.target.value })} required />
        <input placeholder="Department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
        <input placeholder="Position" value={form.position} onChange={(e) => setForm({ ...form, position: e.target.value })} />
        <button type="submit" className="gradient-btn">Add</button>
      </form>

      {/* Link Users to Employee Records */}
      <section className="card form-card">
        <h2>User Accounts</h2>
        {users.length === 0 && <p>No signed-up users yet.</p>}
        {users.map((u) => (
          <div key={u._id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 0', borderBottom: '1px solid #333', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '140px' }}>
              <strong>{u.name}</strong> <span style={{ opacity: 0.7 }}>({u.email})</span>
              <div style={{ fontSize: '0.8em', opacity: 0.7 }}>
                {u.employeeId ? '✅ Linked' : '⚠️ Not linked'}
              </div>
            </div>
            <select
              value={u.employeeId || ''}
              onChange={(e) => handleLinkEmployee(u._id, e.target.value)}
            >
              <option value="">-- No employee record --</option>
              {employees.map((emp) => (
                <option key={emp._id} value={emp._id}>{emp.name} ({emp.email})</option>
              ))}
            </select>
          </div>
        ))}
      </section>

      {/* Employee Salaries List */}
      <section className="grid">
        {employees.length === 0 && <p>No employees yet.</p>}
        {employees.map((emp) => (
          <div className="card employee-card" key={emp._id}>
            <div className="avatar">{emp.name?.[0]?.toUpperCase()}</div>
            <h3>{emp.name}</h3>
            <p className="email">{emp.email}</p>
            <p className="dept">{emp.department} · {emp.position}</p>
            <p className="salary">₹{emp.salary?.toLocaleString()}</p>
          </div>
        ))}
      </section>
    </div>
  );
        }
