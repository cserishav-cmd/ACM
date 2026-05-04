import React, { useRef, useEffect } from "react";
import MarkdownRenderer from "./MarkdownRenderer";

const ChatbotDrawer = ({ isOpen, onClose, messages, isLoading, onSendMessage }) => {
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex justify-end pointer-events-none">
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto" onClick={onClose}></div>
      <aside className="w-full sm:w-[400px] h-full bg-white dark:bg-slate-900 shadow-2xl relative pointer-events-auto flex flex-col animate-slide-in-right contain-paint">
        <div className="h-16 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between shrink-0 bg-primary/5">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
            <h3 className="font-bold text-slate-900 dark:text-slate-100">CropCare Assistant</h3>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 flex items-center justify-center transition-colors">
            <span className="material-symbols-outlined text-slate-500">close</span>
          </button>
        </div>

        <div className="flex-grow overflow-y-auto p-6 space-y-6 hide-scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-30 space-y-4">
              <span className="material-symbols-outlined text-6xl">chat_bubble</span>
              <p className="text-sm font-medium">Hello! Ask me anything about <br/> West Bengal rice farming.</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'ai' ? 'items-start' : 'items-end'}`}>
                <div className={`p-4 rounded-2xl max-w-[85%] text-sm leading-relaxed shadow-sm ${
                  msg.role === 'ai' 
                    ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none border border-slate-200/50' 
                    : 'bg-primary text-white rounded-tr-none'
                }`}>
                  <MarkdownRenderer content={msg.text} animate={msg.role === 'ai' && i === messages.length - 1} />
                </div>
              </div>
            ))
          )}
          <div ref={chatEndRef} />
          {isLoading && (
            <div className="flex gap-1.5 p-2">
              <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.2s]"></div>
              <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.4s]"></div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
           <div className="relative">
              <input 
                type="text" 
                placeholder="Ask about Aman, Boro, fertilizers..." 
                className="w-full pl-4 pr-12 py-4 rounded-2xl bg-slate-100 dark:bg-slate-800 border-none focus:ring-2 focus:ring-primary/20 text-sm transition-all"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if(e.key === 'Enter' && e.target.value.trim() && !isLoading) {
                    onSendMessage(e.target.value.trim());
                    e.target.value = '';
                  }
                }}
              />
              <button 
                className="absolute right-2 top-2 w-10 h-10 bg-primary text-white rounded-xl flex items-center justify-center hover:brightness-110 active:scale-95 transition-all shadow-md"
                onClick={(e) => {
                  const input = e.currentTarget.previousElementSibling;
                  if(input.value.trim() && !isLoading) {
                    onSendMessage(input.value.trim());
                    input.value = '';
                  }
                }}
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
              </button>
           </div>
        </div>
      </aside>
    </div>
  );
};

export default React.memo(ChatbotDrawer);
