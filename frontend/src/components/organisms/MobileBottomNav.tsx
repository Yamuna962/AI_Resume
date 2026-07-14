'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { LayoutDashboard, UploadCloud, Clock, User as UserIcon } from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload', href: '/upload', icon: UploadCloud },
  { name: 'History', href: '/history', icon: Clock },
  { name: 'Profile', href: '/profile', icon: UserIcon },
];

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 flex h-16 items-center justify-around border-t border-border bg-card/95 backdrop-blur-xl md:hidden">
      {navItems.map((item) => {
        const isActive = pathname.startsWith(item.href);

        return (
          <Link
            key={item.name}
            href={item.href}
            className="relative flex flex-1 flex-col items-center justify-center gap-1 py-2"
          >
            {isActive && (
              <motion.div
                layoutId="bottom-nav-active"
                className="absolute inset-x-2 inset-y-1 rounded-lg bg-primary/10"
                initial={false}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
            <item.icon
              className={`relative z-10 h-5 w-5 transition-colors ${
                isActive ? 'text-primary' : 'text-muted-foreground'
              }`}
            />
            <span
              className={`relative z-10 text-[11px] font-medium transition-colors ${
                isActive ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              {item.name}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}