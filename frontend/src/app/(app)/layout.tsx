'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Sparkles } from 'lucide-react';
import { useAuthHydrated, useAuthStore } from '@/stores/auth.store';
import { Sidebar } from '@/components/organisms/Sidebar';
import { TopNavbar } from '@/components/organisms/TopNavbar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, token, logout } = useAuthStore();
  const hydrated = useAuthHydrated();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (hydrated && !token) {
      router.replace('/login');
    }
  }, [hydrated, token, router]);

  if (!hydrated || !token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background font-sans">
        <div className="w-10 h-10 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground font-sans flex">
      {/* Sidebar for md+ screens, hidden on mobile (Sidebar component already handles this) */}
      <Sidebar />

      <div className="flex-1 min-w-0 flex flex-col md:ml-64">
        <TopNavbar />

        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-6xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
}