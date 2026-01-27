import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, BookOpen, User as UserIcon, MessageCircle, Grid, List as ListIcon } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import type { CourseCard } from '../../types';

import { API_BASE_URL } from '../../config';

interface StudentPageProps {
  onSelectCourse: (course: CourseCard) => void;
}

// Academic Course Repository
const COURSE_REPOSITORY: CourseCard[] = [
  {
    id: '1',
    subject: 'Advanced Calculus',
    teacherName: 'Dr. Serikzhanov',
    teacherId: 't1',
    description: 'Deep dive into multivariate functions and vector analysis.',
    materialsCount: 12,
    studentCount: 156,
  },
  {
    id: '2',
    subject: 'Machine Learning',
    teacherName: 'Prof. Alimov',
    teacherId: 't2',
    description: 'Fundamental algorithms and statistical modeling techniques.',
    materialsCount: 24,
    studentCount: 320,
  },
  {
    id: '3',
    subject: 'UI/UX Design',
    teacherName: 'Ms. Kim',
    teacherId: 't3',
    description: 'Principles of modern interface design and user psychology.',
    materialsCount: 8,
    studentCount: 85,
  },
  {
    id: '4',
    subject: 'Network Security',
    teacherName: 'Dr. Ivanov',
    teacherId: 't4',
    description: 'Securing modern infrastructures against cyber threats.',
    materialsCount: 15,
    studentCount: 110,
  }
];

export const StudentPage: React.FC<StudentPageProps> = ({ onSelectCourse }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [courses, setCourses] = useState<CourseCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    const fetchCourses = async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/api/courses`);
        const data = await resp.json();
        // Fallback for empty/new systems
        setCourses(data.length > 0 ? data : COURSE_REPOSITORY);
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        setCourses(COURSE_REPOSITORY);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCourses();
  }, []);

  const filteredCourses = courses.filter(course => 
    course.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.teacherName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      <header className="mb-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 className="text-4xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">
              Academic Library
            </h1>
            <p className="text-lg text-slate-500 dark:text-slate-400 font-medium">
              Find your course assistant and start learning today.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'} 
              size="sm" 
              onClick={() => setViewMode('grid')}
              className="p-2 h-auto rounded-lg"
            >
              <Grid size={18} />
            </Button>
            <Button 
              variant={viewMode === 'list' ? 'secondary' : 'ghost'} 
              size="sm" 
              onClick={() => setViewMode('list')}
              className="p-2 h-auto rounded-lg"
            >
              <ListIcon size={18} />
            </Button>
          </div>
        </div>

        <div className="relative max-w-2xl">
          <Input 
            placeholder="Search by subject or teacher name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search size={20} />}
            className="rounded-2xl py-4 shadow-xl shadow-slate-200/50 dark:shadow-none"
          />
        </div>
      </header>

      <div className={viewMode === 'grid' 
        ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" 
        : "flex flex-col gap-4"
      }>
        <AnimatePresence mode="popLayout">
          {isLoading ? (
            <div className="lg:col-span-3 py-20 flex flex-col items-center justify-center">
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2 }} className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mb-4" />
              <p className="text-slate-400 font-bold animate-pulse uppercase tracking-widest text-xs">Updating Academic Repository</p>
            </div>
          ) : filteredCourses.map((course) => (
            <motion.div
              key={course.id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl overflow-hidden hover:border-blue-500/50 transition-all group shadow-sm hover:shadow-2xl ${
                viewMode === 'list' ? 'flex flex-row items-center p-4' : ''
              }`}
            >
              {viewMode === 'grid' && (
                <div className="h-3 bg-gradient-to-r from-blue-600 to-blue-400" />
              )}
              
              <div className={`p-8 ${viewMode === 'list' ? 'flex-grow py-4' : ''}`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-2xl text-blue-600 mb-4 group-hover:scale-110 transition-transform">
                    <BookOpen size={24} />
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                      Knowledge Verified
                    </span>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                      <span className="text-[10px] font-bold text-green-500 uppercase">Live</span>
                    </div>
                  </div>
                </div>

                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2 leading-tight">
                  {course.subject}
                </h3>
                
                <div className="flex items-center gap-2 mb-4">
                  <UserIcon size={14} className="text-slate-400" />
                  <span className="text-sm font-bold text-slate-600 dark:text-slate-400 underline underline-offset-4 decoration-blue-500/30">
                    {course.teacherName}
                  </span>
                </div>

                <p className="text-slate-500 dark:text-slate-400 text-sm mb-6 line-clamp-2 font-medium">
                  {course.description}
                </p>

                <div className="flex items-center justify-between pt-6 border-t border-slate-100 dark:border-slate-800">
                  <div className="flex gap-4">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Docs</span>
                      <span className="text-sm font-black text-slate-700 dark:text-slate-300">{course.materialsCount}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active</span>
                      <span className="text-sm font-black text-slate-700 dark:text-slate-300">{course.studentCount}</span>
                    </div>
                  </div>
                  <Button 
                    onClick={() => onSelectCourse(course)}
                    className="rounded-xl px-4 py-2 text-xs"
                  >
                    Open Chat <MessageCircle size={14} className="ml-2" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredCourses.length === 0 && (
        <div className="text-center py-20 bg-slate-50 dark:bg-slate-900/50 rounded-[3rem] border-2 border-dashed border-slate-200 dark:border-slate-800">
          <BookOpen className="mx-auto text-slate-300 dark:text-slate-700 mb-4" size={48} />
          <h4 className="text-xl font-bold text-slate-900 dark:text-white">No courses found</h4>
          <p className="text-slate-500">Try searching for another subject or teacher.</p>
        </div>
      )}
    </div>
  );
};
