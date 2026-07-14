'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthHydrated, useAuthStore } from '@/stores/auth.store';
import { Sidebar } from '@/components/organisms/Sidebar';
import { TopNavbar } from '@/components/organisms/TopNavbar';
import { MobileBottomNav } from '@/components/organisms/MobileBottomNav';

// 1. Standalone Guard Component to handle route protection
function AuthGuard({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();
  const hydrated = useAuthHydrated();
  const router = useRouter();

  useEffect(() => {
    if (hydrated && !token) {
      router.replace('/login');
    }
  }, [hydrated, token, router]);

  // Show spinner ONLY during initial hydration or if unauthenticated
  if (!hydrated || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-10 h-10 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  return <>{children}</>;
}

// 2. Layout Component focusing strictly on UI structure
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-background text-foreground font-sans flex">
        {/* Sidebar — hidden on mobile, shown md+ */}
        <Sidebar />
        
        <div className="flex-1 min-w-0 flex flex-col md:ml-64">
          <TopNavbar />

          <main className="flex-1 w-full">
            <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 md:p-8 pb-20 md:pb-8">
              {children}
            </div>
          </main>
        </div>

        <MobileBottomNav />
      </div>
    </AuthGuard>
  );
}
