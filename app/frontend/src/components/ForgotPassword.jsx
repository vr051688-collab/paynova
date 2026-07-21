import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AuthForms.css';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Something went wrong');
      setMessage('OTP sent! Check your Gmail inbox.');
      setTimeout(() => navigate('/reset-password', { state: { email } }), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Forgot Password</h2>
        <p className="auth-subtext">Enter your registered Gmail — we'll send a 6-digit OTP.</p>
        {error && <p className="auth-error">{error}</p>}
        {message && <p className="auth-success">{message}</p>}
        <input type="email" placeholder="Gmail Address" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <button type="submit" disabled={loading}>{loading ? 'Sending...' : 'Send OTP'}</button>
      </form>
    </div>
  );
}
