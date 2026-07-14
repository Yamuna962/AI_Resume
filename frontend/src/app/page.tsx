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
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-cyan-400 flex items-center justify-center">
                <Sparkles size={16} color="white" />
              </div>
              <span className="font-semibold text-lg">AI Resume</span>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/login" className="text-primary hover:underline text-sm font-medium">Sign In</Link>
              <Link href="/login" className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-indigo-600 text-white px-4 py-2 rounded-md text-sm font-semibold shadow-md">Get Started</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden text-center py-20 px-4 sm:py-28">
        <div className="absolute -top-48 left-1/2 transform -translate-x-1/2 w-[60%] h-[60%] rounded-full bg-gradient-to-tr from-primary/20 to-transparent filter blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 left-10 w-48 h-48 rounded-full bg-cyan-500/10 filter blur-2xl pointer-events-none" />

        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-3 bg-primary/10 border border-primary/20 text-primary px-4 py-2 rounded-full mb-6">
            <Sparkles size={14} />
            <span className="text-sm font-medium">Powered by Groq Llama 3.3 + Gemini Flash</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold leading-tight mb-4">
            Beat the ATS &amp; Land <span className="bg-clip-text text-transparent bg-gradient-to-br from-purple-400 to-cyan-400">More Interviews</span>
          </h1>

          <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto mb-8">AI-powered resume analysis that gives you an ATS match score, detects skill gaps, and rewrites your resume to pass any applicant tracking system.</p>

          <div className="flex justify-center gap-4 flex-wrap">
            <Link href="/login" className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-indigo-600 text-white px-5 py-3 rounded-full text-sm font-semibold shadow-lg">
              Analyze My Resume Free <ArrowRight />
            </Link>
            <a href="#how" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground px-4 py-3 rounded-full border border-border">See How It Works</a>
          </div>

          <div className="mt-8 flex items-center justify-center gap-4">
            <div className="flex -space-x-3">
              {['#a78bfa', '#818cf8', '#60a5fa', '#34d399', '#f59e0b'].map((c, i) => (
                <div key={i} className="w-8 h-8 rounded-full border-2 border-background" style={{ background: `linear-gradient(135deg, ${c}, ${c}88)`, marginLeft: i === 0 ? 0 : -8 }} />
              ))}
            </div>
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(i => <Star key={i} size={14} className="text-yellow-400" />)}
            </div>
            <span className="text-sm text-muted-foreground">Trusted by 50,000+ job seekers</span>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-t border-b border-border bg-muted/2">
        <div className="max-w-4xl mx-auto px-4 grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
          {stats.map((s, i) => (
            <div key={i}>
              <div className="text-3xl sm:text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-br from-purple-400 to-cyan-400">{s.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-900/10 border border-cyan-900/20 text-cyan-300 mb-4">
              <Zap size={12} />
              <span className="text-sm font-medium">Features</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold">Everything you need to <span className="bg-clip-text text-transparent bg-gradient-to-br from-purple-400 to-cyan-400">get hired</span></h2>
          </div>

          <div className="grid gap-6 grid-cols-1 md:grid-cols-3">
            {features.map((f, i) => (
              <div key={i} className="p-6 rounded-2xl bg-card border border-border hover:shadow-lg transition-transform transform hover:-translate-y-1">
                <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ background: `${f.color}1A` }}>
                  {f.icon}
                </div>
                <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how" className="py-16 bg-primary/5">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-2xl md:text-3xl font-extrabold mb-4">Three steps to your dream job</h2>
          <p className="text-muted-foreground mb-8">Go from resume upload to AI-powered insights in under 60 seconds.</p>

          <div className="space-y-4">
            {steps.map((s, i) => (
              <div key={i} className="flex items-center gap-4 bg-card border border-border p-4 rounded-lg">
                <div className="min-w-[3rem] h-12 rounded-lg flex items-center justify-center font-bold text-primary" style={{ background: 'linear-gradient(135deg, rgba(124,58,237,0.14), rgba(6,182,212,0.14))' }}>{s.step}</div>
                <div>
                  <h3 className="font-semibold">{s.title}</h3>
                  <p className="text-sm text-muted-foreground">{s.desc}</p>
                </div>
                <CheckCircle2 size={20} className="ml-auto text-primary" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 text-center">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-4">Ready to get <span className="bg-clip-text text-transparent bg-gradient-to-br from-purple-400 to-cyan-400">hired faster?</span></h2>
          <p className="text-muted-foreground mb-8">Join thousands of job seekers who have landed interviews at top companies.</p>
          <Link href="/login" className="inline-flex items-center gap-3 bg-gradient-to-br from-primary to-indigo-600 text-white px-6 py-3 rounded-full text-sm font-semibold shadow-lg">Start For Free — No Credit Card <ArrowRight /></Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center border-t border-border text-muted-foreground">
        © 2026 AI Resume Reviewer. Built with ❤️ using Groq + Gemini AI.
      </footer>
    </div>
  );
}
