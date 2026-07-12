'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  Bell,
  Clock,
  LayoutDashboard,
  LogOut,
  Sparkles,
  UploadCloud,
  User as UserIcon,
} from 'lucide-react';
import { useAuthHydrated, useAuthStore } from '@/stores/auth.store';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload & Analyze', href: '/upload', icon: UploadCloud },
  { name: 'History', href: '/history', icon: Clock },
  { name: 'Profile', href: '/profile', icon: UserIcon },
];

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
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#080812',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        <div
          style={{
            width: '2.5rem',
            height: '2.5rem',
            borderRadius: '50%',
            border: '3px solid rgba(124,58,237,0.3)',
            borderTopColor: '#7c3aed',
            animation: 'spin 1s linear infinite',
          }}
        />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const initials = user?.full_name?.charAt(0)?.toUpperCase() || 'U';

  return (
    <div style={{ minHeight: '100vh', background: '#080812', fontFamily: 'Inter, sans-serif', display: 'flex' }}>
      <aside
        style={{
          width: '240px',
          minWidth: '240px',
          height: '100vh',
          position: 'sticky',
          top: 0,
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(10,10,20,0.95)',
          borderRight: '1px solid rgba(255,255,255,0.06)',
          zIndex: 40,
        }}
      >
        <div style={{ padding: '1.25rem 1.25rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <Link href="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
            <div
              style={{
                width: '2rem',
                height: '2rem',
                borderRadius: '0.625rem',
                background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sparkles size={14} color="white" />
            </div>
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#f0f0ff' }}>AI Resume</span>
          </Link>
        </div>

        <nav style={{ flex: 1, padding: '1rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

            return (
              <Link key={item.name} href={item.href} style={{ textDecoration: 'none' }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.625rem 0.875rem',
                    borderRadius: '0.625rem',
                    background: isActive ? 'rgba(124,58,237,0.15)' : 'transparent',
                    border: isActive ? '1px solid rgba(124,58,237,0.2)' : '1px solid transparent',
                    color: isActive ? '#a78bfa' : '#8888aa',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'all 0.15s ease',
                    cursor: 'pointer',
                  }}
                >
                  <item.icon size={18} />
                  <span>{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        <div style={{ padding: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.625rem 0.75rem',
              borderRadius: '0.625rem',
            }}
          >
            <div
              style={{
                width: '2rem',
                height: '2rem',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 700,
                fontSize: '0.8rem',
                flexShrink: 0,
              }}
            >
              {initials}
            </div>
            <div style={{ overflow: 'hidden', flex: 1 }}>
              <div
                style={{
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#f0f0ff',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user?.full_name || 'User'}
              </div>
              <div
                style={{
                  fontSize: '0.7rem',
                  color: '#8888aa',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user?.email}
              </div>
            </div>
            <button
              onClick={() => {
                logout();
                router.push('/login');
              }}
              title="Logout"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#5a5a7a',
                padding: '0.25rem',
                borderRadius: '0.375rem',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <header
          style={{
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            padding: '0 1.5rem',
            gap: '0.75rem',
            background: 'rgba(8,8,18,0.9)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          <button
            style={{
              width: '2rem',
              height: '2rem',
              borderRadius: '50%',
              border: 'none',
              background: 'rgba(255,255,255,0.05)',
              cursor: 'pointer',
              color: '#8888aa',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            <Bell size={16} />
            <span
              style={{
                position: 'absolute',
                top: '0.25rem',
                right: '0.25rem',
                width: '0.5rem',
                height: '0.5rem',
                borderRadius: '50%',
                background: '#7c3aed',
              }}
            />
          </button>
          <div
            style={{
              width: '2rem',
              height: '2rem',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
            title={user?.full_name || 'User'}
          >
            {initials}
          </div>
        </header>

        <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', width: '100%', margin: '0 auto' }}>{children}</main>
      </div>
    </div>
  );
}
