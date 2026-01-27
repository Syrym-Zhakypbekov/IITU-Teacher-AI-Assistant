import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, Github, User } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

interface AuthPageProps {
  onLogin: () => void;
}

import { API_BASE_URL } from '../../config';

export const AuthPage: React.FC<AuthPageProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');



  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors"
      >
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-slate-500 dark:text-slate-400">
              {isLogin ? 'Enter your details to access your assistant' : 'Join our academic AI community today'}
            </p>
          </div>

          <form className="space-y-5" onSubmit={async (e) => {
             e.preventDefault();
             setIsLoading(true);
             const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
             const body = isLogin ? { email, password } : { email, password, name };
             
             try {
                const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                   method: 'POST',
                   headers: { 'Content-Type': 'application/json' },
                   body: JSON.stringify(body)
                });
                const data = await response.json();
                
                if (response.ok) {
                    if (isLogin) {
                        localStorage.setItem('token', data.token);
                        localStorage.setItem('user_role', data.user.role);
                        onLogin();
                    } else {
                        alert('Registration successful! Please login.');
                        setIsLogin(true);
                    }
                } else {
                    alert(data.detail || 'Authentication failed.');
                }
             } catch (err) {
                 alert('Connection failed.');
             } finally {
                 setIsLoading(false);
             }
          }}>
            {!isLogin && (
                <Input
                  label="Full Name"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  icon={<User size={18} />}
                  required
                />
            )}
            <Input
              label="Email Address"
              type="email"
              placeholder={isLogin ? "name@iitu.kz" : "yourname@iitu.kz (Required for Student)"}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail size={18} />}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              icon={<Lock size={18} />}
              required
            />

            <Button
              type="submit"
              className="w-full py-4 text-base"
              isLoading={isLoading}
            >
              {isLogin ? 'Sign In' : 'Create Account'}
            </Button>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-800"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-slate-900 text-slate-500 transition-colors">
                Or continue with
              </span>
            </div>
          </div>

          <Button
            variant="secondary"
            className="w-full py-3"
          >
            <Github size={20} />
            GitHub
          </Button>
        </div>

        <div className="p-6 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 text-center transition-colors">
          <p className="text-slate-600 dark:text-slate-400">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 font-bold hover:text-blue-700 transition-colors"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
};
