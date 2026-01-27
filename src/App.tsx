import { useState, useEffect, lazy, Suspense, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Layout } from './components/layout/Layout'
import { db, saveAppState, loadAppState } from './db'
import type { View, CourseCard, UserRole } from './types'

// Lazy loaded modules for cost efficiency and speed
const WelcomePage = lazy(() => import('./pages/Welcome/WelcomePage'))
const AuthPage = lazy(() => import('./pages/Auth/AuthPage').then(m => ({ default: m.AuthPage })))
const DashboardPage = lazy(() => import('./pages/Dashboard/DashboardPage').then(m => ({ default: m.DashboardPage })))
const StudentPage = lazy(() => import('./pages/Student/StudentPage').then(m => ({ default: m.StudentPage })))
const ChatInterface = lazy(() => import('./components/chat/ChatInterface').then(m => ({ default: m.ChatInterface })))
const SystemPanel = lazy(() => import('./components/system/SystemPanel').then(m => ({ default: m.SystemPanel })))

// Premium Neural Loader
const PageLoader = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-slate-950">
    <motion.div 
      animate={{ scale: [1, 1.2, 1], opacity: [0.3, 1, 0.3] }}
      transition={{ repeat: Infinity, duration: 2 }}
      className="w-16 h-16 bg-blue-600 rounded-2xl shadow-2xl shadow-blue-500/20"
    />
    <p className="mt-8 text-[10px] font-black uppercase tracking-[0.4em] text-slate-400 animate-pulse">Initializing Neural Core</p>
  </div>
);

function App() {
  const [view, setView] = useState<View>('welcome')
  const [showChat, setShowChat] = useState(false)
  const [activeCourse, setActiveCourse] = useState<CourseCard | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showSystemPanel, setShowSystemPanel] = useState(false)

  // Load state on mount
  useEffect(() => {
    async function init() {
      const saved = await loadAppState();
      const token = localStorage.getItem('token');
      
      // DEEP FIX: If no token in LocalStorage, user is NOT logged in. 
      // This overrides any stale IndexedDB state.
      if (!token) {
          setIsLoggedIn(false);
          setView('welcome');
          saveAppState({ isLoggedIn: false, view: 'welcome' }); // Sync DB
          return;
      }

      if (saved) {
        setView(saved.view);
        setIsLoggedIn(saved.isLoggedIn);
        if (saved.activeCourseId) {
          const course = await db.courses.get(saved.activeCourseId);
          if (course) setActiveCourse(course);
        }
      }
    }
    init();
  }, []);

  // Save state on change
  useEffect(() => {
    saveAppState({
      view,
      isLoggedIn,
      activeCourseId: activeCourse?.id
    });
  }, [view, isLoggedIn, activeCourse]);

  const handleNavigateHome = useCallback(() => {
    setView('welcome');
    setShowChat(false);
    setActiveCourse(null);
  }, []);

  const handleStart = useCallback((selectedRole: UserRole) => {
    if (selectedRole === 'student') {
      setView('student')
    } else {
      if (isLoggedIn) {
        setView('dashboard')
      } else {
        setView('auth')
      }
    }
  }, [isLoggedIn]);

  const handleLogin = useCallback(() => {
    setIsLoggedIn(true)
    setView('dashboard')
  }, []);

  const handleSelectCourse = useCallback((course: CourseCard) => {
    setActiveCourse(course)
    setShowChat(true)
  }, []);

  const handleOpenSystem = useCallback(() => setShowSystemPanel(true), []);
  const handleCloseSystem = useCallback(() => setShowSystemPanel(false), []);
  const handleCloseChat = useCallback(() => setShowChat(false), []);

  const renderView = () => {
    switch (view) {
      case 'welcome':
        return <WelcomePage onStart={handleStart} onOpenSystem={handleOpenSystem} />
      case 'student':
        return (
          <Layout onOpenSystem={handleOpenSystem} onNavigateHome={handleNavigateHome} isLoggedIn={isLoggedIn}>
            <StudentPage onSelectCourse={handleSelectCourse} />
          </Layout>
        )
      case 'auth':
        return (
          <Layout onOpenSystem={handleOpenSystem} onNavigateHome={handleNavigateHome} isLoggedIn={false}>
            <AuthPage onLogin={handleLogin} />
          </Layout>
        )
      case 'dashboard':
        return (
          <Layout onOpenSystem={handleOpenSystem} onNavigateHome={handleNavigateHome} isLoggedIn={isLoggedIn}>
            <DashboardPage 
              activeCourseProp={activeCourse || { id: 'default', subject: 'Architecture', teacherName: 'Teacher' } as CourseCard}
              onChatOpen={async (id) => {
                const course = await db.courses.get(id);
                setActiveCourse(course || { id, subject: 'Course', teacherName: 'Teacher' } as CourseCard);
                setShowChat(true)
              }} 
            />
          </Layout>
        )
      default:
        return <WelcomePage onStart={handleStart} />
    }
  }

  return (
    <div className="app font-academic overflow-x-hidden">
      <Suspense fallback={<PageLoader />}>
        {renderView()}
        
        <AnimatePresence>
          {showSystemPanel && (
            <SystemPanel onClose={handleCloseSystem} />
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showChat && activeCourse && (
            <ChatInterface 
              courseId={activeCourse.id} 
              courseName={activeCourse.subject || 'Course'}
              onClose={handleCloseChat} 
            />
          )}
        </AnimatePresence>
      </Suspense>
    </div>
  )
}

export default App
