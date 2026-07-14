'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthHydrated, useAuthStore } from '@/stores/auth.store';
import { Sidebar } from '@/components/organisms/Sidebar';
import { TopNavbar } from '@/components/organisms/TopNavbar';
import { MobileBottomNav } from '@/components/organisms/MobileBottomNav';

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();
  const hydrated = useAuthHydrated();
  const router = useRouter();

  useEffect(() => {
    if (hydrated && !token) {
      router.replace('/login');
    }
  }, [hydrated, token, router]);

  if (!hydrated || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-10 h-10 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  return <>{children}</>;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      {/* Sidebar: fixed, desktop only */}
      <Sidebar />

      {/* Main column: offset by sidebar width on md+ */}
      <div className="flex min-h-screen flex-col md:ml-64">
        <TopNavbar />

        <main className="flex-1 w-full">
          {/* pb-20 on mobile leaves room above the fixed bottom nav */}
          <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 md:p-8 pb-20 md:pb-8">
            {children}
          </div>
        </main>
      </div>

      {/* Bottom nav: fixed, mobile only */}
      <MobileBottomNav />
    </AuthGuard>
  );
}