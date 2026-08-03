import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function PageShell() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-60 flex-1 p-8">
        <div className="max-w-[1440px] mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}