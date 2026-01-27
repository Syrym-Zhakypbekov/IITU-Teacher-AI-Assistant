import React from 'react';
import { Layout } from '../../components/layout/Layout';
import { FeatureGrid } from '../../components/features/FeatureGrid';
import type { Feature } from '../../components/features/FeatureGrid';
import { BookOpen, Bot, BarChart3, Users, Sparkles, GraduationCap, School } from 'lucide-react';
import { motion } from 'framer-motion';
import type { UserRole } from '../../types';

interface WelcomePageProps {
  onStart: (role: UserRole) => void;
  onOpenSystem?: () => void;
}

const WelcomePage: React.FC<WelcomePageProps> = ({ onStart, onOpenSystem }) => {
  const features: Feature[] = [
    {
      title: 'Course Materials',
      description: 'Access and manage all your academic resources in one organized place.',
      icon: <BookOpen className="w-6 h-6" />,
    },
    {
      title: 'AI Assistant',
      description: 'Interact with our advanced AI trained on specific course content to help you learn.',
      icon: <Bot className="w-6 h-6" />,
    },
    {
      title: 'Smart Analytics',
      description: 'Track your progress and get insights into your academic performance.',
      icon: <BarChart3 className="w-6 h-6" />,
    },
    {
      title: 'Collaborative Learning',
      description: 'Connect with peers and teachers through our integrated communication tools.',
      icon: <Users className="w-6 h-6" />,
    },
  ];

  return (
    <Layout onOpenSystem={onOpenSystem}>
      <div className="relative overflow-hidden bg-white dark:bg-slate-950 transition-colors">
        {/* Background Decorative Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/5 blur-[120px] rounded-full" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/5 blur-[120px] rounded-full" />
        </div>

        {/* Hero Section */}
        <section className="relative pt-20 pb-16 md:pt-32 md:pb-24">
          <div className="container mx-auto px-4 text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-sm font-bold mb-8 border border-blue-100 dark:border-blue-800 shadow-sm"
            >
              <Sparkles size={16} className="animate-pulse" />
              <span>Next Generation Learning</span>
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-5xl md:text-7xl lg:text-8xl font-black text-slate-900 dark:text-white mb-8 leading-tight tracking-tighter"
            >
              IITU Teacher <br />
              <span className="text-blue-600 drop-shadow-sm">AI Assistant</span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="max-w-3xl mx-auto text-lg md:text-2xl text-slate-600 dark:text-slate-400 mb-16 leading-relaxed font-medium"
            >
              Enter the Professional Academic Environment.
              Isolated Knowledge Bases ensure precise, teacher-specific knowledge.
            </motion.p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <button 
                  onClick={() => onStart('student')}
                  className="w-full group p-8 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-[2.5rem] hover:border-blue-500 text-left transition-all hover:shadow-2xl hover:shadow-blue-500/10 active:scale-95"
                >
                  <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center text-blue-600 mb-6 group-hover:scale-110 transition-transform">
                    <GraduationCap size={40} />
                  </div>
                  <h3 className="text-3xl font-black text-slate-900 dark:text-white mb-2">I am a Student</h3>
                  <p className="text-slate-500 dark:text-slate-400 font-bold">Browse courses and chat with specialized assistants.</p>
                </button>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <button 
                  onClick={() => onStart('teacher')}
                  className="w-full group p-8 bg-slate-900 dark:bg-slate-800 border-2 border-slate-700 rounded-[2.5rem] hover:border-blue-500 text-left transition-all hover:shadow-2xl hover:shadow-blue-500/20 active:scale-95"
                >
                  <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform">
                    <School size={40} />
                  </div>
                  <h3 className="text-3xl font-black text-white mb-2">I am a Teacher</h3>
                  <p className="text-slate-400 font-bold">Manage cards, train AI, and upload exclusive materials.</p>
                </button>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-32 bg-slate-50/50 dark:bg-slate-900/50 border-y border-slate-100 dark:border-slate-800/50 transition-colors">
          <div className="container mx-auto px-4">
            <div className="text-center mb-20">
              <h2 className="text-4xl md:text-5xl font-black mb-6 tracking-tight">Powerful Features</h2>
              <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto text-lg font-medium">
                Everything you need to excel in your studies, powered by cutting-edge Academic AI Infrastructure.
              </p>
            </div>
            <FeatureGrid features={features} />
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default WelcomePage;
