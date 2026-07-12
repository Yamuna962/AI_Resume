'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { LayoutDashboard, UploadCloud, Clock, User as UserIcon, Sparkles } from 'lucide-react';
import { useAuthStore } from '@/stores/auth.store';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload & Analyze', href: '/upload', icon: UploadCloud },
  { name: 'History', href: '/history', icon: Clock },
  { name: 'Profile', href: '/profile', icon: UserIcon },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();

  const getInitials = (name: string | null) => {
    if (!name) return 'U';
    return name.charAt(0).toUpperCase();
  };

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-border bg-card md:flex">
      {/* Logo */}
      <div className="flex h-16 items-center px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold tracking-tight">AI Resume</span>
        </Link>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link key={item.name} href={item.href}>
              <div className={`relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive ? 'text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}>
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-primary/10"
                    initial={false}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon className={`h-5 w-5 relative z-10 ${isActive ? 'text-primary' : ''}`} />
                <span className="relative z-10">{item.name}</span>
              </div>
            </Link>
          );
        })}
      </div>

      {/* User */}
      <div className="border-t border-border p-4">
        <Link href="/profile">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-muted">
            <Avatar className="h-9 w-9 border border-border">
              <AvatarImage src={user?.avatar_url || ''} />
              <AvatarFallback className="bg-primary/10 text-primary">
                {getInitials(user?.full_name || null)}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col overflow-hidden">
              <span className="truncate text-sm font-medium">{user?.full_name || 'User'}</span>
              <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
            </div>
          </div>
        </Link>
      </div>
    </aside>
  );
}
