import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await login(form.username, form.password);
      navigate('/');
    } catch {
      setError('Usuário ou senha inválidos.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: 'linear-gradient(135deg, #1e40af, #3b82f6)' }}>
      <div className="card p-4" style={{ width: 360 }}>
        <div className="text-center mb-4">
          <i className="bi bi-building-check" style={{ fontSize: '3rem', color: '#1e40af' }}></i>
          <h4 className="mt-2 fw-bold">Gestor de Visitas</h4>
          <p className="text-muted small">Sistema de Gestão de Visitas às Escolas</p>
        </div>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Usuário</label>
            <input className="form-control" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required autoFocus />
          </div>
          <div className="mb-3">
            <label className="form-label">Senha</label>
            <input type="password" className="form-control" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />
          </div>
          <button className="btn btn-primary w-100" type="submit" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : <i className="bi bi-box-arrow-in-right me-2" />}
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}
