import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PageShell } from './components/layout/PageShell';
import { DashboardPage } from './pages/DashboardPage';
import { CustomerListPage } from './pages/CustomerListPage';
import { CustomerDetailPage } from './pages/CustomerDetailPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PageShell />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/customers" element={<CustomerListPage />} />
          <Route path="/customers/:id" element={<CustomerDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}