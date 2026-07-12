'use client';

import Link from 'next/link';
import { ArrowRight, Sparkles, Zap, Target, Brain, Star, CheckCircle2, Upload } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: <Target size={24} />,
      title: 'ATS Score Analysis',
      desc: 'Get an instant score showing how well your resume matches the job description.',
      color: '#7c3aed',
    },
    {
      icon: <Brain size={24} />,
      title: 'AI Rewrite Engine',
      desc: 'Our AI rewrites weak sections to be more impactful and keyword-rich.',
      color: '#06b6d4',
    },
    {
      icon: <Zap size={24} />,
      title: 'Skill Gap Detection',
      desc: 'Instantly see which required skills are missing from your resume.',
      color: '#f59e0b',
    },
  ];

  const steps = [
    { step: '01', title: 'Upload Resume', desc: 'Upload your resume PDF in seconds.', icon: <Upload size={20} /> },
    { step: '02', title: 'Paste Job Description', desc: 'Add the job posting you are applying for.', icon: <Target size={20} /> },
    { step: '03', title: 'Get AI Analysis', desc: 'Receive an ATS score, skill gaps, and smart rewrites.', icon: <Sparkles size={20} /> },
  ];

  const stats = [
    { value: '94%', label: 'ATS Pass Rate' },
    { value: '3x', label: 'More Interviews' },
    { value: '50K+', label: 'Resumes Analyzed' },
    { value: '<30s', label: 'Analysis Time' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#080812', fontFamily: "'Inter', sans-serif", color: '#f0f0ff' }}>
      {/* Navbar */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '1.25rem 2rem', position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(8,8,18,0.85)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '2.25rem', height: '2.25rem', borderRadius: '0.625rem',
            background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Sparkles size={16} color="white" />
          </div>
          <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>AI Resume</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Link href="/login" style={{
            padding: '0.5rem 1.25rem', borderRadius: '0.625rem',
            color: '#a78bfa', textDecoration: 'none', fontWeight: 500, fontSize: '0.9rem',
            transition: 'color 0.2s',
          }}>
            Sign In
          </Link>
          <Link href="/login" style={{
            padding: '0.5rem 1.25rem', borderRadius: '0.625rem',
            background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
            color: 'white', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem',
            boxShadow: '0 4px 15px rgba(124,58,237,0.3)',
            transition: 'all 0.2s',
          }}>
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        textAlign: 'center', padding: '6rem 2rem 5rem', position: 'relative', overflow: 'hidden',
      }}>
        {/* Background glows */}
        <div style={{
          position: 'absolute', top: '-20%', left: '50%', transform: 'translateX(-50%)',
          width: '60%', height: '60%', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(124,58,237,0.2) 0%, transparent 70%)',
          filter: 'blur(60px)', pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: '-10%', left: '10%',
          width: '30%', height: '40%', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%)',
          filter: 'blur(40px)', pointerEvents: 'none',
        }} />

        {/* Badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          padding: '0.375rem 1rem', borderRadius: '99px',
          background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.25)',
          fontSize: '0.8rem', color: '#a78bfa', fontWeight: 600, marginBottom: '2rem',
        }}>
          <Sparkles size={14} />
          Powered by Groq Llama 3.3 + Gemini Flash
        </div>

        <h1 style={{
          fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
          fontWeight: 900, lineHeight: 1.1, marginBottom: '1.5rem',
          letterSpacing: '-0.02em', position: 'relative',
        }}>
          Beat the ATS &amp; Land{' '}
          <span style={{
            background: 'linear-gradient(135deg, #a855f7 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
          }}>
            More Interviews
          </span>
        </h1>

        <p style={{
          fontSize: 'clamp(1rem, 2vw, 1.25rem)', color: '#8888aa',
          maxWidth: '600px', margin: '0 auto 3rem', lineHeight: 1.7,
        }}>
          AI-powered resume analysis that gives you an ATS match score, detects skill gaps,
          and rewrites your resume to pass any applicant tracking system.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link href="/login" style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.875rem 2rem', borderRadius: '0.875rem',
            background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
            color: 'white', textDecoration: 'none', fontWeight: 700,
            fontSize: '1rem', boxShadow: '0 8px 30px rgba(124,58,237,0.35)',
            transition: 'all 0.2s',
          }}>
            Analyze My Resume Free
            <ArrowRight size={20} />
          </Link>
          <Link href="#how" style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.875rem 2rem', borderRadius: '0.875rem',
            background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
            color: '#c4c4e0', textDecoration: 'none', fontWeight: 600, fontSize: '1rem',
            transition: 'all 0.2s',
          }}>
            See How It Works
          </Link>
        </div>

        {/* Social proof */}
        <div style={{ marginTop: '2.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ display: 'flex' }}>
            {['#a78bfa', '#818cf8', '#60a5fa', '#34d399', '#f59e0b'].map((c, i) => (
              <div key={i} style={{
                width: '2rem', height: '2rem', borderRadius: '50%',
                background: `linear-gradient(135deg, ${c}, ${c}88)`,
                border: '2px solid #080812', marginLeft: i > 0 ? '-0.5rem' : 0,
              }} />
            ))}
          </div>
          <div style={{ display: 'flex', gap: '0.25rem', marginLeft: '0.5rem' }}>
            {[1,2,3,4,5].map(i => <Star key={i} size={14} fill="#f59e0b" color="#f59e0b" />)}
          </div>
          <span style={{ color: '#8888aa', fontSize: '0.85rem' }}>Trusted by 50,000+ job seekers</span>
        </div>
      </section>

      {/* Stats */}
      <section style={{
        padding: '3rem 2rem',
        borderTop: '1px solid rgba(255,255,255,0.04)',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        background: 'rgba(255,255,255,0.01)',
      }}>
        <div style={{
          maxWidth: '900px', margin: '0 auto',
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '2rem',
          textAlign: 'center',
        }}>
          {stats.map((s, i) => (
            <div key={i}>
              <div style={{
                fontSize: '2.5rem', fontWeight: 900,
                background: 'linear-gradient(135deg, #a855f7, #06b6d4)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              }}>
                {s.value}
              </div>
              <div style={{ color: '#8888aa', fontSize: '0.9rem', marginTop: '0.25rem' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '6rem 2rem' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.375rem 1rem', borderRadius: '99px',
              background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.2)',
              fontSize: '0.8rem', color: '#22d3ee', fontWeight: 600, marginBottom: '1.5rem',
            }}>
              <Zap size={12} /> Features
            </div>
            <h2 style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', fontWeight: 800, letterSpacing: '-0.02em' }}>
              Everything you need to{' '}
              <span style={{
                background: 'linear-gradient(135deg, #a855f7, #06b6d4)',
                WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              }}>
                get hired
              </span>
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {features.map((f, i) => (
              <div key={i} style={{
                padding: '2rem',
                background: 'rgba(15,15,26,0.8)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: '1.25rem',
                transition: 'all 0.3s ease',
              }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLElement).style.border = `1px solid ${f.color}44`;
                  (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 40px ${f.color}22`;
                  (e.currentTarget as HTMLElement).style.transform = 'translateY(-4px)';
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLElement).style.border = '1px solid rgba(255,255,255,0.06)';
                  (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                  (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                }}
              >
                <div style={{
                  width: '3rem', height: '3rem', borderRadius: '0.875rem', marginBottom: '1.5rem',
                  background: `${f.color}18`, border: `1px solid ${f.color}33`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: f.color,
                }}>
                  {f.icon}
                </div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>{f.title}</h3>
                <p style={{ color: '#8888aa', lineHeight: 1.7, fontSize: '0.9rem' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how" style={{ padding: '6rem 2rem', background: 'rgba(124,58,237,0.04)' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', fontWeight: 800, marginBottom: '1rem', letterSpacing: '-0.02em' }}>
            Three steps to your dream job
          </h2>
          <p style={{ color: '#8888aa', marginBottom: '4rem', fontSize: '1rem' }}>
            Go from resume upload to AI-powered insights in under 60 seconds.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {steps.map((s, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '1.5rem', textAlign: 'left',
                padding: '1.5rem 2rem',
                background: 'rgba(15,15,26,0.9)',
                border: '1px solid rgba(124,58,237,0.12)',
                borderRadius: '1rem',
              }}>
                <div style={{
                  minWidth: '3rem', height: '3rem', borderRadius: '0.75rem',
                  background: 'linear-gradient(135deg, #7c3aed22, #06b6d422)',
                  border: '1px solid rgba(124,58,237,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#a78bfa', fontSize: '0.75rem', fontWeight: 800,
                }}>
                  {s.step}
                </div>
                <div>
                  <h3 style={{ fontWeight: 700, marginBottom: '0.25rem' }}>{s.title}</h3>
                  <p style={{ color: '#8888aa', fontSize: '0.9rem' }}>{s.desc}</p>
                </div>
                <CheckCircle2 size={20} color="#7c3aed" style={{ marginLeft: 'auto', flexShrink: 0 }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '6rem 2rem', textAlign: 'center', position: 'relative' }}>
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at center, rgba(124,58,237,0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <h2 style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)', fontWeight: 900, letterSpacing: '-0.02em', marginBottom: '1.5rem', position: 'relative' }}>
          Ready to get{' '}
          <span style={{
            background: 'linear-gradient(135deg, #a855f7, #06b6d4)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            hired faster?
          </span>
        </h2>
        <p style={{ color: '#8888aa', maxWidth: '500px', margin: '0 auto 2.5rem', fontSize: '1.1rem', lineHeight: 1.7, position: 'relative' }}>
          Join thousands of job seekers who have landed interviews at top companies.
        </p>
        <Link href="/login" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          padding: '1rem 2.5rem', borderRadius: '0.875rem',
          background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
          color: 'white', textDecoration: 'none', fontWeight: 700, fontSize: '1.05rem',
          boxShadow: '0 8px 30px rgba(124,58,237,0.4)',
          position: 'relative',
        }}>
          Start For Free — No Credit Card
          <ArrowRight size={20} />
        </Link>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '2rem', textAlign: 'center',
        borderTop: '1px solid rgba(255,255,255,0.04)',
        color: '#5a5a7a', fontSize: '0.85rem',
      }}>
        © 2026 AI Resume Reviewer. Built with ❤️ using Groq + Gemini AI.
      </footer>
    </div>
  );
}
