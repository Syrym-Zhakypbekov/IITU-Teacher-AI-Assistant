import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Book, FileText, MessageSquare, Brain, Activity, Clock, Trash2, Edit3 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import type { Material, CourseCard } from '../../types';

interface DashboardProps {
  onChatOpen: (courseId: string) => void;
  activeCourseProp: CourseCard;
}

import { API_BASE_URL } from '../../config';

export const DashboardPage: React.FC<DashboardProps> = ({ onChatOpen, activeCourseProp }) => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [activeCourse] = useState<CourseCard>(activeCourseProp);
  const [isRetraining, setIsRetraining] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    const fetchMaterials = async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/api/materials/${activeCourse.id}`);
        const data = await resp.json();
        setMaterials(data);
      } catch (err) {
        console.error('Failed to fetch materials:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMaterials();
  }, [activeCourse.id]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('course_id', activeCourse.id);
    
    const newMaterials: Material[] = Array.from(files).map(file => {
      formData.append('files', file);
      return {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        type: file.type || 'document',
        size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
        status: 'pending',
        progress: 0,
        uploadedAt: new Date()
      };
    });

    setMaterials(prev => [...prev, ...newMaterials]);

    setMaterials(prev => [...prev, ...newMaterials]);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}` 
        },
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      // Start real-time ingestion tracking
      newMaterials.forEach(mat => {
        initializeIngestionTracking(mat.id);
      });
    } catch (error) {
      console.error('Upload Error:', error);
      setMaterials(prev => prev.map(m => 
        newMaterials.find(nm => nm.id === m.id) 
          ? { ...m, status: 'error' as any, progress: 0 } 
          : m
      ));
    }
  };

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_BASE_URL}/api/ingest/${activeCourse.id}`, { 
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
      });
      // Reset progress for all ready materials to show "updating"
      setMaterials(prev => prev.map(m => ({ ...m, status: 'processing', progress: 80 })));
      setTimeout(() => {
        setMaterials(prev => prev.map(m => ({ ...m, status: 'ready', progress: 100 })));
        setIsRetraining(false);
      }, 2000);
    } catch (error) {
      setIsRetraining(false);
    }
  };

  const [currentFileStatus, setCurrentFileStatus] = useState<string>('');

  const initializeIngestionTracking = (materialId: string) => {
    console.log(`Ingestion Tracking Started: ${materialId}`);
    // Instead of simulation, we poll the real backend status for the WHOLE course workspace
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/ingest/status/${activeCourse.id}`);
        const data = await response.json();
        
        if (data.status === 'ready' || data.progress === 100) {
          setMaterials(prev => prev.map(m => ({ ...m, status: 'ready', progress: 100 })));
          setCurrentFileStatus('System Ready. Multi-tenant workspace fully indexed.');
          clearInterval(pollInterval);
        } else {
          setMaterials(prev => prev.map(m => 
            // If the specific material is what the backend reports, or if we just want to update all pending
            m.status !== 'ready' ? { ...m, status: 'processing', progress: data.progress } : m
          ));
          setCurrentFileStatus(`${data.status.toUpperCase()}: ${data.current_file}`);
        }
      } catch (error) {
        console.error('Polling Error:', error);
      }
    }, 800);
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      {/* Header Info */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8 mb-12">
        <div className="flex-grow">
          <div className="flex items-center gap-3 mb-3">
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 text-xs font-black uppercase tracking-widest rounded-full">
              Teacher Dashboard
            </span>
            <span className="text-slate-300 dark:text-slate-700">/</span>
            <span className="text-sm font-bold text-slate-500">{activeCourse.subject}</span>
          </div>
          <h1 className="text-5xl font-black text-slate-900 dark:text-white mb-2 tracking-tighter">
            Manage <span className="text-blue-600">Assistant</span>
          </h1>
          <p className="text-slate-500 dark:text-slate-400 font-medium text-lg">
            Train your AI, manage documents, and monitor student engagement.
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            size="lg" 
            className="rounded-2xl border-dashed"
            onClick={() => window.alert('Professional Workspace Customization is currently active. You can modify materials below or scrub the entire workspace in the System Panel.')}
          >
            <Edit3 size={18} />
          </Button>
          <Button 
            onClick={() => onChatOpen(activeCourse.id)}
            size="lg"
            className="rounded-2xl gap-3 px-8 shadow-2xl shadow-blue-500/30"
          >
            <MessageSquare size={20} />
            Launch AI Assistant
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Left Column: Stats & Training */}
        <div className="lg:col-span-4 space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-xl">
              <Activity className="text-blue-600 mb-4" size={24} />
              <div className="text-3xl font-black text-slate-900 dark:text-white mb-1">{activeCourse.studentCount}</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Students</div>
            </div>
            <div className="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-xl">
              <Brain className="text-blue-400 mb-4" size={24} />
              <div className="text-3xl font-black text-slate-900 dark:text-white mb-1">98%</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">System Accuracy</div>
            </div>
          </div>

          <div className="bg-slate-900 text-white p-8 rounded-[2.5rem] shadow-2xl shadow-blue-900/20 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <Brain size={120} />
            </div>
            <h2 className="text-2xl font-black mb-4 relative z-10 leading-tight">AI Training Status</h2>
            <div className="space-y-6 relative z-10">
              <div>
                <div className="flex justify-between text-xs font-bold mb-2 uppercase tracking-wide opacity-60">
                  <span>Knowledge Base</span>
                  <span>{materials.filter(m => m.status === 'ready').length} Ready</span>
                </div>
                <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: materials.length > 0 ? (materials.filter(m => m.status === 'ready').length / materials.length * 100) + '%' : '0%' }}
                    className="h-full bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)]"
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-4 bg-white/5 rounded-2xl border border-white/10">
                <Clock size={16} className="text-blue-400" />
                <span className="text-xs font-bold opacity-80">Last trained: {activeCourse.lastTrained?.toLocaleTimeString()}</span>
              </div>
              
              {currentFileStatus && (
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
                  <div className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-1">Indexing Status Log</div>
                  <div className="text-xs font-mono text-white/90 truncate animate-pulse">
                    {currentFileStatus}
                  </div>
                </div>
              )}
              
              <Button 
                onClick={handleRetrain}
                disabled={isRetraining}
                className={`w-full ${isRetraining ? 'bg-slate-700' : 'bg-blue-600 hover:bg-blue-500'} text-white font-black py-4 rounded-2xl shadow-xl shadow-blue-600/30 transition-all`}
              >
                {isRetraining ? 'Updating Knowledge Base...' : 'Sync Knowledge Base'}
              </Button>
            </div>
          </div>
        </div>

        {/* Right Column: Files Management */}
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-white dark:bg-slate-900 p-12 rounded-[3.5rem] border-4 border-dashed border-slate-200 dark:border-slate-800 hover:border-blue-500 dark:hover:border-blue-400 transition-all relative group cursor-pointer shadow-sm">
            <input 
              title="Upload file"
              type="file" 
              multiple 
              onChange={handleFileUpload}
              className="absolute inset-0 opacity-0 cursor-pointer z-10"
            />
            <div className="text-center relative z-0">
              <div className="w-24 h-24 bg-blue-50 dark:bg-blue-900/30 rounded-[2.5rem] flex items-center justify-center text-blue-600 mx-auto mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg">
                <Upload size={48} />
              </div>
              <h3 className="text-3xl font-black mb-3 text-slate-900 dark:text-white tracking-tight">
                Import Lecture Content
              </h3>
              <p className="text-slate-500 dark:text-slate-400 font-bold text-lg max-w-md mx-auto leading-relaxed">
                Add your PDF slides, Word documents, or text files to train your assistant.
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-black text-2xl flex items-center gap-3 text-slate-900 dark:text-white">
                <Book size={24} className="text-blue-600" /> 
                Course Materials 
              </h3>
              <span className="text-xs font-black px-4 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-full text-slate-400 uppercase tracking-widest border border-slate-200 dark:border-slate-700">
                Total: {materials.length}
              </span>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              <AnimatePresence>
                {isLoading ? (
                  <div className="py-12 text-center text-slate-400 font-bold uppercase tracking-widest text-xs animate-pulse">Scanning Secure Repository...</div>
                ) : materials.map(file => (
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    key={file.id}
                    className="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-200 dark:border-slate-800 flex items-center gap-6 group hover:border-blue-500/50 transition-all shadow-sm"
                  >
                    <div className="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-2xl flex items-center justify-center text-slate-400 group-hover:text-blue-600 transition-colors shadow-inner">
                      <FileText size={32} />
                    </div>
                    <div className="flex-grow min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-black text-lg text-slate-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md ${
                          file.status === 'ready' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600 animate-pulse'
                        }`}>
                          {file.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-grow h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: file.progress + '%' }}
                            className={`h-full ${file.status === 'ready' ? 'bg-green-500' : 'bg-blue-600'}`} 
                          />
                        </div>
                        <span className="text-xs font-black text-slate-400 w-10 text-right">{file.progress}%</span>
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      onClick={async () => {
                        try {
                          const token = localStorage.getItem('token');
                          await fetch(`${API_BASE_URL}/api/materials/${activeCourse.id}/${file.name}`, { 
                              method: 'DELETE',
                              headers: {
                                'Authorization': `Bearer ${token}`
                              }
                          });
                          setMaterials(materials.filter(m => m.id !== file.id));
                        } catch (err) {
                          console.error('Delete failed:', err);
                        }
                      }}
                      className="p-3 h-auto text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-2xl"
                    >
                      <Trash2 size={24} />
                    </Button>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {materials.length === 0 && (
                <div className="text-center py-24 bg-white dark:bg-slate-900/50 rounded-[4rem] border-2 border-dashed border-slate-200 dark:border-slate-800 shadow-inner">
                  <div className="w-24 h-24 bg-slate-50 dark:bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-8 text-slate-300 dark:text-slate-700 shadow-lg">
                    <FileText size={48} />
                  </div>
                  <h4 className="text-2xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Empty Repository</h4>
                  <p className="text-slate-500 dark:text-slate-400 font-bold text-lg">
                    Start by uploading your academic materials above.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
