import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Escolas from './pages/Escolas';
import Visitas from './pages/Visitas';
import NovaVisita from './pages/NovaVisita';
import DetalhesVisita from './pages/DetalhesVisita';
import Agenda from './pages/Agenda';
import Mapa from './pages/Mapa';
import Distancias from './pages/Distancias';
import Relatorios from './pages/Relatorios';
import Mediadores from './pages/Mediadores';

function PrivateRoute({ children }) {
  const { user } = useAuth();
  if (user === undefined) return <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-primary"></div></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();
  if (user === undefined) return <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-primary"></div></div>;

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/escolas" element={<Escolas />} />
        <Route path="/visitas" element={<Visitas />} />
        <Route path="/visitas/nova" element={<NovaVisita />} />
        <Route path="/visitas/:id" element={<DetalhesVisita />} />
        <Route path="/agenda" element={<Agenda />} />
        <Route path="/mapa" element={<Mapa />} />
        <Route path="/distancias" element={<Distancias />} />
        <Route path="/relatorios" element={<Relatorios />} />
        <Route path="/mediadores" element={<Mediadores />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
