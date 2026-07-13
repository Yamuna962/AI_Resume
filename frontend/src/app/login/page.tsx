'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Sparkles, Mail, Lock, Eye, EyeOff, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { useAuthStore } from '@/stores/auth.store';
import api from '@/lib/axios';
import { getApiErrorMessage, isNetworkError } from '@/lib/api-error';
import type { User } from '@/types';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export default function LoginPage() {
  const router = useRouter();
  const { token, setToken, setUser } = useAuthStore();

  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) router.replace('/dashboard');
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError('');
  setLoading(true);

  try {
    if (mode === 'register') {
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
      });
    }

    const res = await api.post<LoginResponse>('/auth/login', {
      email,
      password,
    });

    const accessToken = res.data.access_token;
    const userData = res.data.user;

    setToken(accessToken);
    setUser(userData);

    await new Promise((r) => setTimeout(r, 50));

    router.replace('/dashboard');

  } catch (error: unknown) {
    console.error("LOGIN ERROR:", error);

    if (isNetworkError(error)) {
      setError(
        error instanceof Error
          ? error.message
          : JSON.stringify(error)
      );
    } else {
      setError(
        getApiErrorMessage(
          error,
          'Something went wrong. Please try again.'
        )
      );
    }

  } finally {
    setLoading(false);
  }
};

  return (
    <div style={{
      minHeight: '100vh',
      background: '#080812',
      fontFamily: "'Inter', -apple-system, sans-serif",
      color: '#f0f0ff',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background glow effects */}
      <div style={{
        position: 'fixed', top: '-10%', left: '50%', transform: 'translateX(-50%)',
        width: '70%', height: '50%', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%)',
        filter: 'blur(80px)', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'fixed', bottom: '0', right: '-10%',
        width: '40%', height: '40%', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%)',
        filter: 'blur(60px)', pointerEvents: 'none',
      }} />

      {/* Logo */}
      <Link href="/" style={{
        display: 'flex', alignItems: 'center', gap: '0.625rem',
        textDecoration: 'none', marginBottom: '2.5rem',
      }}>
        <div style={{
          width: '2.25rem', height: '2.25rem', borderRadius: '0.625rem',
          background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(124,58,237,0.35)',
        }}>
          <Sparkles size={16} color="white" />
        </div>
        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f0f0ff' }}>AI Resume</span>
      </Link>

      {/* Card */}
      <div style={{
        width: '100%',
        maxWidth: '420px',
        background: 'rgba(15,15,26,0.9)',
        border: '1px solid rgba(124,58,237,0.15)',
        borderRadius: '1.5rem',
        padding: '2.5rem',
        backdropFilter: 'blur(20px)',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{
            fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.02em',
            marginBottom: '0.5rem',
          }}>
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h1>
          <p style={{ color: '#8888aa', fontSize: '0.875rem' }}>
            {mode === 'login'
              ? 'Sign in to your AI Resume account'
              : 'Start optimizing your resume today'}
          </p>
        </div>

        {/* Mode Toggle */}
        <div style={{
          display: 'flex', background: 'rgba(0,0,0,0.3)',
          borderRadius: '0.75rem', padding: '0.25rem', marginBottom: '1.75rem',
          border: '1px solid rgba(255,255,255,0.05)',
        }}>
          {(['login', 'register'] as const).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(''); }}
              style={{
                flex: 1, padding: '0.5rem', borderRadius: '0.5rem', border: 'none',
                fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: mode === m
                  ? 'linear-gradient(135deg, #7c3aed, #4f46e5)'
                  : 'transparent',
                color: mode === m ? '#ffffff' : '#8888aa',
                boxShadow: mode === m ? '0 2px 12px rgba(124,58,237,0.3)' : 'none',
              }}
            >
              {m === 'login' ? 'Sign In' : 'Sign Up'}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {mode === 'register' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#c4c4e0', marginBottom: '0.375rem' }}>
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="John Smith"
                required
                style={{
                  width: '100%', background: 'rgba(13,13,22,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem',
                  padding: '0.75rem 1rem', color: '#f0f0ff', fontSize: '0.9rem',
                  outline: 'none', fontFamily: 'Inter, sans-serif',
                  transition: 'all 0.2s ease', boxSizing: 'border-box',
                }}
                onFocus={e => {
                  e.target.style.borderColor = 'rgba(124,58,237,0.6)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(124,58,237,0.1)';
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.08)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          )}

          {/* Email */}
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#c4c4e0', marginBottom: '0.375rem' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{
                position: 'absolute', left: '0.875rem', top: '50%', transform: 'translateY(-50%)',
                color: '#5a5a7a', pointerEvents: 'none',
              }} />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                style={{
                  width: '100%', background: 'rgba(13,13,22,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem',
                  padding: '0.75rem 1rem 0.75rem 2.5rem', color: '#f0f0ff', fontSize: '0.9rem',
                  outline: 'none', fontFamily: 'Inter, sans-serif',
                  transition: 'all 0.2s ease', boxSizing: 'border-box',
                }}
                onFocus={e => {
                  e.target.style.borderColor = 'rgba(124,58,237,0.6)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(124,58,237,0.1)';
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.08)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#c4c4e0', marginBottom: '0.375rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{
                position: 'absolute', left: '0.875rem', top: '50%', transform: 'translateY(-50%)',
                color: '#5a5a7a', pointerEvents: 'none',
              }} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder={mode === 'register' ? 'Min 8 chars, include a number' : '••••••••'}
                required
                minLength={mode === 'register' ? 8 : undefined}
                style={{
                  width: '100%', background: 'rgba(13,13,22,0.8)',
                  border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem',
                  padding: '0.75rem 2.75rem 0.75rem 2.5rem', color: '#f0f0ff', fontSize: '0.9rem',
                  outline: 'none', fontFamily: 'Inter, sans-serif',
                  transition: 'all 0.2s ease', boxSizing: 'border-box',
                }}
                onFocus={e => {
                  e.target.style.borderColor = 'rgba(124,58,237,0.6)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(124,58,237,0.1)';
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'rgba(255,255,255,0.08)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: '0.875rem', top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: '#5a5a7a', display: 'flex', alignItems: 'center', padding: 0,
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {mode === 'register' && (
              <p style={{ marginTop: '0.375rem', fontSize: '0.75rem', color: '#666688' }}>
                Use at least 8 characters with letters and a number (e.g. MyPass123)
              </p>
            )}
          </div>

          {/* Error */}
          {error && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.625rem',
              padding: '0.75rem 1rem', borderRadius: '0.75rem',
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
              color: '#f87171', fontSize: '0.85rem',
            }}>
              <AlertCircle size={15} style={{ flexShrink: 0 }} />
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '0.25rem',
              padding: '0.875rem',
              borderRadius: '0.75rem',
              background: loading ? 'rgba(124,58,237,0.5)' : 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              color: 'white', border: 'none',
              fontWeight: 700, fontSize: '0.95rem', cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
              boxShadow: loading ? 'none' : '0 4px 20px rgba(124,58,237,0.35)',
              transition: 'all 0.2s ease',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {loading ? (
              <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                {mode === 'login' ? 'Signing in…' : 'Creating account…'}
              </>
            ) : (
              <>{mode === 'login' ? 'Sign In' : 'Create Account'} <ArrowRight size={16} /></>
            )}
          </button>

          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </form>

        {/* Footer link */}
        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: '#8888aa' }}>
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: '#a78bfa', fontWeight: 600, fontSize: '0.85rem',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {mode === 'login' ? 'Sign up free' : 'Sign in'}
          </button>
        </p>
      </div>

      <p style={{ marginTop: '1.5rem', color: '#5a5a7a', fontSize: '0.8rem', textAlign: 'center' }}>
        Trusted by 50,000+ job seekers · No credit card required
      </p>
    </div>
  );
}
