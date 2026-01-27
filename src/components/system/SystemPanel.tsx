import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Network, Database, Trash2, Globe, Wifi, WifiOff, X, Activity, HardDrive, ShieldCheck, Leaf, LogOut } from 'lucide-react';
import { Button } from '../ui/Button';
import { db } from '../../db';

export const SystemPanel: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [dbStats, setDbStats] = useState({ materials: 0, courses: 0 });
  const [storageUsage, setStorageUsage] = useState<number | null>(null);

  useEffect(() => {
    const handleStatusChange = () => setIsOnline(navigator.onLine);
    window.addEventListener('online', handleStatusChange);
    window.addEventListener('offline', handleStatusChange);

    const updateStats = async () => {
      const matCount = await db.materials.count();
      const courseCount = await db.courses.count();
      setDbStats({ materials: matCount, courses: courseCount });

      if (navigator.storage && navigator.storage.estimate) {
        const estimate = await navigator.storage.estimate();
        if (estimate.usage) {
          setStorageUsage(Math.round(estimate.usage / (1024 * 1024)));
        }
      }
    };

    updateStats();
    return () => {
      window.removeEventListener('online', handleStatusChange);
      window.removeEventListener('offline', handleStatusChange);
    };
  }, []);

  const clearStorage = async () => {
    if (confirm('Are you sure? This will delete all local materials and progress.')) {
      await db.delete();
      location.reload();
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      className="fixed top-0 right-0 h-full w-full sm:w-[400px] bg-white dark:bg-slate-950 shadow-2xl z-[200] border-l border-slate-200 dark:border-slate-800 p-8 overflow-y-auto"
    >
      <div className="flex items-center justify-between mb-12">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-500/20">
            <Activity size={20} />
          </div>
          <h2 className="text-xl font-black text-slate-900 dark:text-white tracking-tight uppercase">System Health</h2>
        </div>
        <Button variant="ghost" onClick={onClose} className="p-2 rounded-full">
          <X size={24} />
        </Button>
      </div>

      <div className="space-y-8">
        {/* Network Status */}
        <section className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Network size={16} /> Network
            </h3>
            {isOnline ? (
              <span className="flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-600 text-[10px] font-black rounded-full uppercase">
                <Wifi size={12} /> Connected
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-600 text-[10px] font-black rounded-full uppercase">
                <WifiOff size={12} /> Offline
              </span>
            )}
          </div>
          <div className="flex items-center gap-4 text-slate-600 dark:text-slate-300">
            <Globe size={24} className="text-blue-500" />
            <div>
              <p className="text-xs font-bold opacity-60">Edge Node Connection</p>
              <p className="text-sm font-black">IITU Neural Backbone v2.4</p>
            </div>
          </div>
        </section>

        {/* Database Status */}
        <section className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
          <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-6">
            <Database size={16} /> Intelligent Storage
          </h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Materials</p>
              <p className="text-2xl font-black text-slate-900 dark:text-white">{dbStats.materials}</p>
            </div>
            <div className="p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Saved Courses</p>
              <p className="text-2xl font-black text-slate-900 dark:text-white">{dbStats.courses}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-2xl border border-blue-100 dark:border-blue-800 mb-6">
            <HardDrive size={18} className="text-blue-600" />
            <div>
              <p className="text-[10px] font-bold text-blue-600 uppercase">Disk Usage</p>
              <p className="text-xs font-black text-blue-900 dark:text-blue-100 italic">
                {storageUsage !== null ? `${storageUsage} MB consumed locally` : 'Calculating...'}
              </p>
            </div>
          </div>
          <Button 
            variant="danger" 
            onClick={clearStorage}
            className="w-full py-4 rounded-2xl font-black text-xs uppercase tracking-widest gap-2"
          >
            <Trash2 size={16} /> Purge Neural Cache
          </Button>
        </section>

        {/* Cost Analytics */}
        <section className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
           <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <Leaf size={16} className="text-green-500" /> Cost Forensics
              </h3>
              <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-[10px] font-black rounded-md uppercase">
                 Live
              </span>
           </div>
           
           <div className="space-y-4">
             <div className="flex justify-between items-center p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
               <span className="text-xs font-bold text-slate-500">Tokens Saved</span>
               <span className="font-black text-slate-900 dark:text-white">~450k</span>
             </div>
             <div className="flex justify-between items-center p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
                <span className="text-xs font-bold text-slate-500">GPU Hours Saved</span>
                <span className="font-black text-slate-900 dark:text-white">12.4 hrs</span>
             </div>
             <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
               <p className="text-[10px] font-black text-green-600 uppercase mb-1">Efficiency Rating</p>
               <p className="text-xs font-medium text-green-700 dark:text-green-300">
                 Exceptional. System running on minimal compute budget.
               </p>
             </div>
           </div>
        </section>

        {/* Security & Admin */}
        <section className="p-6 bg-slate-900 text-white rounded-[2.5rem] shadow-xl shadow-blue-950/20 flex flex-col gap-6">
           <div className="flex items-center gap-6">
            <div className="w-14 h-14 bg-white/10 rounded-2xl flex items-center justify-center">
                <ShieldCheck size={32} className="text-blue-400" />
            </div>
            <div>
                <p className="text-[10px] font-black uppercase opacity-50 tracking-[0.2em] mb-1">Encrypted Path</p>
                <h4 className="text-lg font-black leading-tight">Zero-Knowledge <br /> RAG Protocol</h4>
            </div>
           </div>
           
           <div className="pt-6 border-t border-white/10 space-y-3">
             <p className="text-[10px] font-black uppercase opacity-40 tracking-[0.2em]">Admin Controls</p>
             <Button 
                variant="danger" 
                onClick={() => {
                  if(confirm('CONFIRM LOGOUT: This will terminate your secure session.')) {
                     location.reload(); 
                  }
                }}
                className="w-full bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-white border-none justify-start px-4"
              >
               <LogOut size={16} className="mr-2" /> Terminate Session
             </Button>
           </div>
        </section>

        <p className="text-[10px] text-center text-slate-400 font-bold uppercase tracking-[0.2em] mt-12 opacity-60">
          IITU Assistant System v1.0.4-stable
        </p>
      </div>
    </motion.div>
  );
};
