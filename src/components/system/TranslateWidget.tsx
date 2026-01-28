
import React, { useEffect, useState } from 'react';
import { Languages, Check } from 'lucide-react';
import { Button } from '../ui/Button';

declare global {
  interface Window {
    google: any;
    googleTranslateElementInit: any;
  }
}

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'kk', label: 'Қазақша', flag: '🇰🇿' }
];

export const TranslateWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState('en');

  useEffect(() => {
    // 1. Initialize Google Translate (Hidden)
    window.googleTranslateElementInit = () => {
      new window.google.translate.TranslateElement(
        {
          pageLanguage: 'en',
          autoDisplay: false,
          includedLanguages: 'en,ru,kk', 
        },
        'google_translate_element'
      );
    };

    // 2. Load script
    if (!document.getElementById('google-translate-script')) {
      const script = document.createElement('script');
      script.id = 'google-translate-script';
      script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
      script.async = true;
      document.body.appendChild(script);
    }

    // 3. Check current language from cookie
    const match = document.cookie.match(/googtrans=\/en\/([a-z]{2})/);
    if (match) setCurrentLang(match[1]);
  }, []);

  const changeLanguage = (langCode: string) => {
    // Set Google Translate Cookie
    // Format: /sourceLang/targetLang
    document.cookie = `googtrans=/en/${langCode}; path=/; domain=${window.location.hostname}`;
    document.cookie = `googtrans=/en/${langCode}; path=/;`; // Fallback
    
    setCurrentLang(langCode);
    setIsOpen(false);
    window.location.reload(); // Reload to apply translation
  };

  return (
    <div className="relative flex items-center">
        {/* Toggle Button */}
        <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className={`p-2 transition-colors ${isOpen ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20' : 'text-slate-500 hover:text-blue-600'}`}
            title="Change Language"
        >
            <Languages size={20} />
            <span className="ml-2 text-xs font-bold uppercase hidden lg:block">{currentLang}</span>
        </Button>

        {/* Custom Dropdown */}
        {isOpen && (
            <>
                <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                <div className="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 overflow-hidden">
                    <div className="p-2 border-b border-slate-100 dark:border-slate-800">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 py-1">
                            Select Language
                        </div>
                    </div>
                    <div className="p-1">
                        {LANGUAGES.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => changeLanguage(lang.code)}
                                className={`w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                                    currentLang === lang.code 
                                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' 
                                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                                }`}
                            >
                                <span className="flex items-center gap-2">
                                    <span className="text-lg">{lang.flag}</span>
                                    {lang.label}
                                </span>
                                {currentLang === lang.code && <Check size={14} />}
                            </button>
                        ))}
                    </div>
                </div>
            </>
        )}

        {/* Hidden Container for Google Logic */}
        <div id="google_translate_element" className="hidden"></div>
    </div>
  );
};
