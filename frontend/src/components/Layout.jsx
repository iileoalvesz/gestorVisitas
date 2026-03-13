import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark" style={{ background: 'linear-gradient(135deg, #1e40af, #3b82f6)' }}>
        <div className="container-fluid">
          <NavLink className="navbar-brand fw-bold" to="/">
            <i className="bi bi-building-check me-2"></i>Gestor de Visitas
          </NavLink>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navMain">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <NavLink className="nav-link" to="/" end>
                  <i className="bi bi-house me-1"></i>Início
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/escolas">
                  <i className="bi bi-building me-1"></i>Escolas
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/agenda">
                  <i className="bi bi-calendar-week me-1"></i>Agenda
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/visitas">
                  <i className="bi bi-clipboard-check me-1"></i>Visitas
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/mapa">
                  <i className="bi bi-map me-1"></i>Mapa
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/distancias">
                  <i className="bi bi-pin-map me-1"></i>Distâncias
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/relatorios">
                  <i className="bi bi-file-earmark-bar-graph me-1"></i>Relatórios
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink className="nav-link" to="/mediadores">
                  <i className="bi bi-people me-1"></i>Mediadores
                </NavLink>
              </li>
            </ul>
            <ul className="navbar-nav">
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  <i className="bi bi-person-circle me-1"></i>{user?.nome_exibicao || user?.username}
                </a>
                <ul className="dropdown-menu dropdown-menu-end">
                  <li><button className="dropdown-item text-danger" onClick={handleLogout}>
                    <i className="bi bi-box-arrow-right me-1"></i>Sair
                  </button></li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <main className="py-4">
        <Outlet />
      </main>
    </>
  );
}
