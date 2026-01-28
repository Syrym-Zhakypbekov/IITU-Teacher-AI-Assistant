
import React, { useEffect, useState } from 'react';
import { Languages } from 'lucide-react';
import { Button } from '../ui/Button';

declare global {
  interface Window {
    google: any;
    googleTranslateElementInit: any;
  }
}

export const TranslateWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // 1. Define Initialization Function
    window.googleTranslateElementInit = () => {
      new window.google.translate.TranslateElement(
        {
          pageLanguage: 'en',
          layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
          autoDisplay: false,
        },
        'google_translate_element'
      );
    };

    // 2. Load Script if not present
    if (!document.getElementById('google-translate-script')) {
      const script = document.createElement('script');
      script.id = 'google-translate-script';
      script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
      script.async = true;
      document.body.appendChild(script);
    }
  }, []);

  return (
    <div className="relative flex items-center">
        {/* Toggle Button */}
        <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className={`p-2 transition-colors ${isOpen ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20' : 'text-slate-500 hover:text-blue-600'}`}
            title="Translate Page"
        >
            <Languages size={20} />
        </Button>

        {/* Hidden/Pop-up Container */}
        <div 
             className={`absolute top-full right-0 mt-2 p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 transition-all duration-200 origin-top-right ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0 pointer-events-none'}`}
             style={{ minWidth: '200px' }}
        >
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 px-1">
                Select Language
            </div>
            {/* Google's Container */}
            <div id="google_translate_element" className="google-translate-container"></div>
            
            {/* Styling Override for Google's messy UI */}
            <style>{`
                .goog-te-gadget-simple {
                    background-color: transparent !important;
                    border: none !important;
                    font-family: inherit !important;
                    padding: 0 !important;
                }
                .goog-te-gadget-simple span {
                    color: inherit !important;
                }
                iframe.goog-te-banner-frame { display: none !important; }
                body { top: 0px !important; }
                
                /* Dark Mode Support for the widget text */
                :global(.dark) .goog-te-gadget-simple span {
                    color: #94a3b8 !important;
                }
            `}</style>
        </div>
    </div>
  );
};
