'use client';

import Link from 'next/link';
import { Bell, Menu, X, LayoutDashboard, UploadCloud, Clock, User as UserIcon, Sparkles } from 'lucide-react';
import { ThemeToggle } from '@/components/atoms/ThemeToggle';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuthStore } from '@/stores/auth.store';
import { useRouter, usePathname } from 'next/navigation';
import { Dialog, DialogTrigger, DialogContent, DialogClose } from '@/components/ui/dialog';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload & Analyze', href: '/upload', icon: UploadCloud },
  { name: 'History', href: '/history', icon: Clock },
  { name: 'Profile', href: '/profile', icon: UserIcon },
];

export function TopNavbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/80 px-4 md:px-6 backdrop-blur-xl md:justify-end">
      {/* Mobile Menu - visible only on small screens */}
      <Dialog>
        <DialogTrigger asChild>
          <div className="md:hidden">
            <Button variant="ghost" size="icon" aria-label="Open menu">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </DialogTrigger>
        <DialogContent className="w-full max-w-sm p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Sparkles className="h-5 w-5" />
              </div>
              <span className="text-lg font-bold tracking-tight">AI Resume</span>
            </div>
            <DialogClose asChild>
              <Button variant="ghost" size="icon" aria-label="Close menu">
                <X className="h-4 w-4" />
              </Button>
            </DialogClose>
          </div>

          <nav className="mt-4 flex flex-col gap-2">
            {navItems.map((item) => {
              const isActive = pathname?.startsWith(item.href);
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${isActive ? 'text-primary bg-primary/10' : 'text-foreground hover:bg-muted'}`}
                >
                  <Icon className={`h-5 w-5 ${isActive ? 'text-primary' : 'text-muted-foreground'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-6 border-t border-border pt-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-9 w-9 border border-border">
                <AvatarImage src={user?.avatar_url || ''} />
                <AvatarFallback className="bg-primary/10 text-primary">{user?.full_name?.charAt(0) || 'U'}</AvatarFallback>
              </Avatar>
              <div className="flex flex-col overflow-hidden">
                <span className="truncate text-sm font-medium">{user?.full_name || 'User'}</span>
                <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
              </div>
            </div>

            <div className="mt-3 flex gap-2">
              <Button variant="outline" size="sm" onClick={() => router.push('/profile')}>Profile</Button>
              <Button variant="destructive" size="sm" onClick={handleLogout}>Logout</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger className="relative h-8 w-8 rounded-full flex items-center justify-center cursor-pointer hover:bg-muted/20 transition-colors outline-none border-none">
            <Avatar className="h-8 w-8 border border-border">
              <AvatarImage src={user?.avatar_url || ''} />
              <AvatarFallback className="bg-primary/10 text-primary">
                {user?.full_name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push('/profile')}>
              Profile Settings
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout} className="text-destructive">
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
