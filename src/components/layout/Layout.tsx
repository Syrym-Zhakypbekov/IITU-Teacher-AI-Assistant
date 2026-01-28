import { GraduationCap, ArrowRight, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';
import { ThemeToggle } from '../theme/ThemeToggle';
import { Button } from '../ui/Button';
import { TranslateWidget } from '../system/TranslateWidget';

interface LayoutProps {
  children: React.ReactNode;
  onOpenSystem?: () => void;
  onNavigateHome?: () => void;
  isLoggedIn?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ children, onOpenSystem, onNavigateHome, isLoggedIn }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors duration-300 font-academic">
      <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 glass-effect">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <motion.div 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 cursor-pointer group" 
            onClick={onNavigateHome}
          >
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 group-hover:rotate-6 transition-transform">
              <GraduationCap size={24} />
            </div>
            <span className="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400 tracking-tighter">
              IITU AI
            </span>
          </motion.div>
          
          <nav className="flex items-center gap-3 md:gap-6">
            <div className="hidden md:flex items-center gap-6 mr-2">
              <a 
                href={onNavigateHome ? "#" : "#features"} 
                onClick={(e) => {
                  if (onNavigateHome) {
                    e.preventDefault();
                    onNavigateHome();
                    // Optional: add a timeout to scroll after navigation
                    setTimeout(() => {
                      const el = document.getElementById('features');
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                    }, 100);
                  }
                }}
                className="text-xs font-bold text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors uppercase tracking-widest"
              >
                Features
              </a>
            </div>
            
            
            <div className="flex items-center gap-2">
               <TranslateWidget />
               <ThemeToggle />
            </div>
            
            {onOpenSystem && (
              <div className="flex items-center gap-2">
                <Button 
                  onClick={onOpenSystem}
                  size="sm" 
                  className="hidden sm:flex rounded-full px-6 text-xs uppercase tracking-widest font-black"
                >
                  System <ArrowRight size={14} className="ml-2" />
                </Button>
              </div>
            )}
            
            {isLoggedIn && (
                <Button 
                  variant="ghost"
                  size="sm"
                  onClick={async () => {
                    if (window.confirm('Terminate Session?')) {
                      localStorage.removeItem('token');
                      localStorage.removeItem('user_role');
                      // DEEP FIX: Clear persistent DB state
                      const { saveAppState } = await import('../../db');
                      await saveAppState({ isLoggedIn: false, view: 'welcome' }); 
                      window.location.reload();
                    }
                  }}
                  className="p-2 text-slate-400 hover:text-red-500 transition-colors"
                  title="Log Out"
                >
                  <LogOut size={20} />
                </Button>
            )}
          </nav>

          <Button variant="ghost" className="md:hidden p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          </Button>
        </div>
      </header>

      <main className="flex-grow">
        {children}
      </main>

      <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-12">
            <div className="flex flex-col items-center md:items-start gap-4">
              <div className="flex items-center gap-2 opacity-80">
                <GraduationCap size={24} className="text-blue-600" />
                <span className="text-lg font-black tracking-tight text-slate-900 dark:text-white uppercase text-center">IITU Assistant</span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 font-medium max-w-xs text-center md:text-left">
                Next-generation learning platform with teacher-specific Knowledge Indexing.
              </p>
            </div>
            <div className="flex flex-col md:flex-row items-center gap-8 md:gap-16">
              <div className="flex gap-8 text-sm font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">
                <a href="#" className="hover:text-blue-600 transition-colors">Privacy</a>
                <a href="#" className="hover:text-blue-600 transition-colors">Terms</a>
                <a href="#" className="hover:text-blue-600 transition-colors">Status</a>
              </div>
              <p className="text-sm text-slate-400 dark:text-slate-600 font-bold">
                &copy; {new Date().getFullYear()} IITU. PRODUCTION v1.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
