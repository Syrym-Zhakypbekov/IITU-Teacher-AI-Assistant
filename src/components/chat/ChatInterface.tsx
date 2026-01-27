import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, User, Bot, Sparkles, MoveLeft, Volume2, VolumeX, History, Plus, MessageSquare } from 'lucide-react';
import { db } from '../../db';
import { Button } from '../ui/Button';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  courseId: string;
  courseName: string;
  onClose: () => void;
}

import { API_BASE_URL } from '../../config';

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ courseId, courseName, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello! I am your AI Assistant for ${courseName}. I have indexed the specific materials for this course. How can I help you?`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [useAudio, setUseAudio] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [queueStatus, setQueueStatus] = useState<{pos: number, wait: number} | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load History on Mount
  const [forumMessages, setForumMessages] = useState<any[]>([]);
  const [isGuest, setIsGuest] = useState(false);

  // Load History & Forum on Mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsGuest(!token);

    const loadData = async () => {
      // 1. Local Private History
      const localItems = await db.chatHistory.where('courseId').equals(courseId).reverse().sortBy('timestamp');
      setHistoryItems(localItems);

      // 2. Public Forum History (Shared)
      try {
          const headers: Record<string, string> = {};
          if (token) headers['Authorization'] = `Bearer ${token}`;
          
          const res = await fetch(`${API_BASE_URL}/api/chat/history/${courseId}`, { headers });
          if (res.ok) {
              const forumData = await res.json();
              setForumMessages(forumData);
          }
      } catch (e) { console.error("Forum load failed", e); }
    };
    loadData();
  }, [courseId]);

  // Save Session on Unmount or Change
  const saveSession = async () => {
     if (messages.length <= 1) return; // Don't save empty welcome chats
     const title = messages[1]?.content.slice(0, 40) + "..." || "New Chat";
     await db.chatHistory.add({
         courseId,
         title,
         timestamp: new Date(),
         messages
     });
  };
  
  const handleLoadSession = (sessionMessages: Message[]) => {
      setMessages(sessionMessages);
      setShowHistory(false);
  };

  const handleNewChat = async () => {
    await saveSession(); // archive current
    const items = await db.chatHistory.where('courseId').equals(courseId).reverse().sortBy('timestamp');
    setHistoryItems(items); // update list
    setMessages([{
      id: Date.now().toString(),
      role: 'assistant',
      content: `Hello! I am your AI Assistant for ${courseName}. How can I help you today?`,
      timestamp: new Date()
    }]);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    const currentAudioMode = useAudio;
    // Don't clear input if this is a retry/poll, but here we are starting fresh
    if (!ticketId) {
        setInput('');
    }
    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
        },
        body: JSON.stringify({
          message: currentInput,
          course_id: courseId,
          is_voice: currentAudioMode,
          ticket_id: ticketId 
        }),
      });

      if (!response.ok) throw new Error('Connection timeout');

      const data = await response.json();
      
      // QUEUE HANDLING
      if (data.status === 'queued') {
          setTicketId(data.ticket_id);
          setQueueStatus({ pos: data.position, wait: data.wait_time });
          
          // Poll again in 2 seconds
          setTimeout(() => {
              handleSend(); 
          }, 2000);
          return; // Stay in typing state
      }

      // Success! Clear queue state
      setTicketId(null);
      setQueueStatus(null);
      
      const aiMsg: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: "I'm having trouble connecting to the AI Service. Please ensure the local backend is running.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed inset-0 z-[100] bg-white dark:bg-slate-950 flex flex-col sm:m-4 sm:rounded-[2.5rem] sm:shadow-2xl sm:border sm:border-slate-200 sm:dark:border-slate-800 overflow-hidden transition-colors"
    >
      <div className="h-20 px-8 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={onClose} className="p-2 rounded-full text-slate-500">
            <MoveLeft size={20} />
          </Button>
          <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            <Bot size={28} />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-900 dark:text-white leading-tight">{courseName}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-[10px] font-bold text-slate-500 uppercase">Workspace ID: {courseId}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={handleNewChat} className="hidden sm:flex text-slate-500 hover:text-blue-600" title="New Chat">
            <Plus size={20} />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setShowHistory(!showHistory)} className="text-slate-500 hover:text-blue-600 relative">
            <History size={20} />
            {historyItems.length > 0 && <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-blue-500 rounded-full border-2 border-white dark:border-slate-900" />}
          </Button>
          <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 mx-1 hidden sm:block" />
          <Button 
            variant={useAudio ? 'secondary' : 'ghost'} 
            size="sm" 
            onClick={() => setUseAudio(!useAudio)}
            className={`rounded-xl gap-2 px-3 border transition-colors ${useAudio ? 'border-blue-500 bg-blue-50 text-blue-600' : 'border-slate-200 text-slate-400'}`}
          >
            {useAudio ? <Volume2 size={18} /> : <VolumeX size={18} />}
            <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">
              {useAudio ? 'Audio High-Fidelity' : 'Standard Text'}
            </span>
          </Button>

          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 rounded-full text-xs font-bold border border-blue-100 dark:border-blue-800 shadow-sm">
            {queueStatus ? (
                <span className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                    </span>
                    Queue #{queueStatus.pos} ({Math.ceil(queueStatus.wait)}s)
                </span>
            ) : (
                <><Sparkles size={14} className="animate-pulse" /> AI Status</>
            )}
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-grow overflow-y-auto p-8 space-y-8 scroll-smooth">
        
        {/* PUBLIC FORUM HISTORY (Shared Knowledge) */}
        {forumMessages.length > 0 && (
            <div className="mb-12 border-b-2 border-slate-100 dark:border-slate-800 pb-8">
                <div className="flex items-center justify-center gap-2 mb-8 opacity-50">
                    <div className="h-px bg-slate-300 w-24"></div>
                    <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">Student Community Forum</span>
                    <div className="h-px bg-slate-300 w-24"></div>
                </div>
                {forumMessages.map((msg, idx) => (
                    <div key={`forum-${idx}`} className="space-y-4 mb-8 opacity-90 hover:opacity-100 transition-opacity">
                        {/* Question */}
                        <div className="flex gap-4 items-start">
                            <div className="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center flex-shrink-0">
                                <span className="font-bold text-xs">{msg.user_name.charAt(0)}</span>
                            </div>
                            <div className="bg-orange-50/50 dark:bg-orange-900/10 p-4 rounded-2xl rounded-tl-none border border-orange-100 dark:border-orange-800/30">
                                <div className="text-[10px] font-bold text-orange-400 uppercase tracking-widest mb-1">{msg.user_name} asked:</div>
                                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{msg.question}</p>
                            </div>
                        </div>
                        {/* Answer */}
                        <div className="flex gap-4 items-start ml-8">
                            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 w-full">
                                <div className="flex items-center gap-2 mb-2">
                                    <Sparkles size={12} className="text-blue-500" />
                                    <span className="text-[10px] font-bold text-slate-400 uppercase">AI Answer</span>
                                </div>
                                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{msg.answer}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        )}

        {/* CURRENT SESSION */}
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-4 max-w-[85%] md:max-w-[75%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-slate-100 dark:bg-slate-800 text-slate-600' : 'bg-blue-600 text-white'}`}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className={`p-5 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 rounded-tl-none border border-slate-200 dark:border-slate-800'}`}>
                <p className="text-[15px] leading-relaxed font-medium">{msg.content}</p>
                <p className="text-[10px] mt-3 font-bold opacity-40 uppercase tracking-widest">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
              </div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white mr-4 shadow-lg shadow-blue-500/20">
              <Bot size={20} />
            </div>
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl rounded-tl-none border border-slate-200 dark:border-slate-800 flex items-center gap-1.5 shadow-sm">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-duration:0.6s]" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-duration:0.6s] [animation-delay:0.2s]" />
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-duration:0.6s] [animation-delay:0.4s]" />
            </div>
          </div>
        )}
      </div>


      {/* HISTORY SIDEBAR */}
      {showHistory && (
        <motion.div 
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            className="absolute top-20 left-0 bottom-0 w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 z-[90] shadow-2xl overflow-y-auto"
        >
            <div className="p-4">
                <h4 className="font-black text-xs uppercase tracking-widest text-slate-400 mb-4 ml-2">Recent Chats</h4>
                <div className="space-y-2">
                    <Button variant="secondary" className="w-full justify-start gap-2 mb-4" onClick={handleNewChat}>
                        <Plus size={16} /> New Chat
                    </Button>
                    {historyItems.map((item) => (
                        <button 
                            key={item.id}
                            onClick={() => handleLoadSession(item.messages)}
                            className="w-full text-left p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-start gap-3 group"
                        >
                            <MessageSquare size={16} className="mt-1 text-slate-400 group-hover:text-blue-500 transition-colors" />
                            <div>
                                <p className="text-sm font-bold text-slate-700 dark:text-slate-300 line-clamp-1">{item.title}</p>
                                <p className="text-[10px] font-medium text-slate-400">{item.timestamp.toLocaleDateString()}</p>
                            </div>
                        </button>
                    ))}
                    {historyItems.length === 0 && (
                        <p className="text-center text-slate-400 text-xs py-10">No history yet.</p>
                    )}
                </div>
            </div>
        </motion.div>
      )}

      <div className="p-8 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto flex items-end gap-3 px-5 py-4 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[1.5rem] shadow-sm">
          <textarea 
            title="Message input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder={isGuest ? "Search community questions (Guest Mode)..." : "Ask a question to the class AI..."}
            className="flex-grow bg-transparent border-none outline-none resize-none py-2 text-base text-slate-800 dark:text-white"
            rows={1}
          />
          <Button onClick={handleSend} disabled={!input.trim()} className="p-3 bg-blue-600 text-white rounded-xl">
            <Send size={20} />
          </Button>
        </div>
      </div>
    </motion.div>
  );
};
