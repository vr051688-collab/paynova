import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiFetch } from '../api';

export default function EmployeeDashboard() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const emp = await apiFetch('/api/employees');
        setProfile(emp?.[0] || null);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <p>Loading your dashboard...</p>;
  if (!profile) return <p>No employee record linked to your account yet. Contact your admin.</p>;

  const chartData = (profile.performanceHistory || []).sort((a, b) => a.month.localeCompare(b.month));

  return (
    <div className="dashboard">
      <section className="card profile-card">
        <div className="avatar large">{profile.name?.[0]?.toUpperCase()}</div>
        <h2>{profile.name}</h2>
        <p className="dept">{profile.department} · {profile.position}</p>
        <p className="salary big">₹{profile.salary?.toLocaleString()} / month</p>
      </section>

      <section className="card chart-card">
        <h2>My Performance</h2>
        {chartData.length === 0 ? (
          <p>No performance data recorded yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#dc2743" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
}
