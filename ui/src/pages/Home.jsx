import { useState, useRef, useEffect, useCallback } from "react";
import Loader from "../components/Loader";
import Result from "../components/Result";
import OrderPage from "../components/OrderPage";
import { predictPaddy, predictGrain, sendChatMessage } from "../services/api";
import WeatherForecast from "../components/WeatherForecast";
import Logo from "../components/Logo";
import ExpenseCalculator from "../components/ExpenseCalculator";
import ChatbotDrawer from "../components/ChatbotDrawer";

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [scanType, setScanType] = useState('paddy');
  const [currentView, setCurrentView] = useState('dashboard');
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPercent = Math.min(window.scrollY / 400, 1);
      document.documentElement.style.setProperty('--scroll-blur', `${scrollPercent * 12}px`);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleFileSelected = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const response = scanType === 'grain' ? await predictGrain(selectedFile) : await predictPaddy(selectedFile);
      if (response.success) {
        setResult(response.data);
      } else {
        setError(response.message || "Prediction failed.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Connection error.");
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleSendMessage = useCallback(async (text) => {
    if (!text.trim()) return;
    setChatMessages(prev => [...prev, { role: 'user', text }]);
    setIsChatLoading(true);
    try {
      const response = await sendChatMessage([...chatMessages, { role: 'user', text }], result);
      if (response.success) {
        setChatMessages(prev => [...prev, { role: 'ai', text: response.data.reply }]);
      }
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsChatLoading(false);
    }
  }, [chatMessages, result]);
  
  if (loading) return <Loader />;
  if (currentView === 'market') return <OrderPage onBack={() => setCurrentView('dashboard')} />;

  if (currentView === 'calculator') return (
    <div className="bg-background text-on-background min-h-screen contain-layout">
      <header className="bg-white/90 dark:bg-slate-950/90 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-5 h-16 w-full">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentView('dashboard')}>
          <span className="material-symbols-outlined">arrow_back</span>
          <Logo className="h-10" />
        </div>
      </header>
      <main className="px-container-padding py-stack-md max-w-5xl mx-auto pb-32">
        <ExpenseCalculator 
          aiData={result} 
          onAnalyze={(summary) => {
            setShowChat(true);
            handleSendMessage(`Calculated: ${summary}. Suggest actions?`);
          }}
        />
      </main>
      <BottomNav active="calculator" setView={setCurrentView} />
    </div>
  );

  if (result) return <Result data={result} file={file} onReset={() => setResult(null)} onMarket={() => setCurrentView('market')} />;

  return (
    <div className="bg-background text-on-background min-h-screen pb-32 contain-layout">
      <header className="bg-white/90 dark:bg-slate-950/90 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-5 h-16 w-full">
        <Logo className="h-10" />
        <button 
          onClick={() => setShowChat(!showChat)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${showChat ? 'bg-primary text-white border-primary shadow-lg' : 'hover:bg-slate-100 border-slate-200'}`}
        >
          <span className="font-label-md text-label-md">Assistant</span>
          <span className="material-symbols-outlined text-[18px]">{showChat ? 'close' : 'smart_toy'}</span>
        </button>
      </header>

      <main className="px-container-padding py-stack-md max-w-4xl mx-auto space-y-stack-md">
        {error && <ErrorBanner message={error} onClose={() => setError(null)} />}
        
        <section className="animate-fade-in">
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-stack-sm">
            {getGreeting()}
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">Your farm's status at a glance.</p>
        </section>

        <WeatherForecast />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
          <ScanCard 
            title="Paddy Health" 
            desc="Detect diseases from leaf images." 
            bg="bg-primary-container" 
            textColor="text-white"
            btn="Scan Paddy" 
            icon="psychiatry"
            onClick={() => { setScanType('paddy'); triggerFileInput(); }} 
          />
          <ScanCard 
            title="Rice Variety" 
            desc="Identify grains via AI vision." 
            bg="bg-orange-100 dark:bg-orange-950/30" 
            textColor="text-on-surface"
            btn="Identify Grains" 
            icon="grain"
            onClick={() => { setScanType('grain'); triggerFileInput(); }} 
          />
        </div>

        <div className="grid grid-cols-2 gap-gutter">
          <ActionButton label="Add Crop" icon="add_circle" color="text-primary" />
          <ActionButton label="Calculator" icon="calculate" color="text-secondary" onClick={() => setCurrentView('calculator')} />
        </div>

        <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileSelected} accept="image/*" />
      </main>

      <BottomNav active="dashboard" setView={setCurrentView} />
      
      <ChatbotDrawer 
        isOpen={showChat} 
        onClose={() => setShowChat(false)} 
        messages={chatMessages} 
        isLoading={isChatLoading} 
        onSendMessage={handleSendMessage} 
      />
    </div>
  );
}

// Sub-components for better performance and readability
const ScanCard = ({ title, desc, bg, btn, icon, onClick, textColor = "text-on-surface" }) => (
  <div className={`relative rounded-xl overflow-hidden shadow-sm group h-full ${bg} contain-paint`}>
    <div className="relative z-10 flex flex-col p-6 sm:p-8 h-full justify-between">
      <div>
        <h2 className={`font-headline-lg text-headline-lg ${textColor} mb-2`}>{title}</h2>
        <p className={`font-body-md text-body-md ${textColor === 'text-white' ? 'text-white/80' : 'text-on-surface-variant/80'}`}>{desc}</p>
      </div>
      <button onClick={onClick} className="bg-primary text-on-primary px-6 py-4 rounded-full inline-flex items-center justify-center gap-2 hover:bg-primary/90 transition-all active:scale-95 shadow-md self-start mt-6">
        <span className="material-symbols-outlined">{icon}</span>
        {btn}
      </button>
    </div>
  </div>
);

const ActionButton = ({ label, icon, color, onClick }) => (
  <button onClick={onClick} className="bg-surface-container-lowest border border-outline-variant rounded-lg p-4 flex flex-col items-center justify-center gap-2 hover:bg-surface-container transition-colors shadow-sm">
    <span className={`material-symbols-outlined ${color} text-[28px]`}>{icon}</span>
    <span className="font-label-md text-label-md text-on-surface">{label}</span>
  </button>
);

const BottomNav = ({ active, setView }) => (
  <nav className="md:hidden bg-white dark:bg-slate-950 fixed bottom-0 w-full z-50 border-t border-slate-100 flex justify-around items-center h-20 px-4 pb-safe">
    <NavItem active={active === 'dashboard'} icon="potted_plant" label="Crops" onClick={() => setView('dashboard')} />
    <NavItem active={active === 'calculator'} icon="calculate" label="Calculator" onClick={() => setView('calculator')} />
    <NavItem active={active === 'market'} icon="storefront" label="Market" onClick={() => setView('market')} />
  </nav>
);

const NavItem = ({ active, icon, label, onClick }) => (
  <button onClick={onClick} className={`flex flex-col items-center justify-center px-3 py-1 transition-all ${active ? 'text-primary' : 'text-slate-400'}`}>
    <span className={`material-symbols-outlined mb-1 ${active ? 'icon-fill' : ''}`}>{icon}</span>
    <span className="text-[10px] font-bold uppercase">{label}</span>
  </button>
);

const ErrorBanner = ({ message, onClose }) => (
  <div className="bg-error-container text-error px-4 py-3 rounded-lg flex justify-between items-center mb-4 border border-error/20 animate-slide-in-top">
    <div className="flex items-center gap-2">
      <span className="material-symbols-outlined icon-fill">warning</span>
      <span className="font-label-md text-label-md">{message}</span>
    </div>
    <button onClick={onClose} className="hover:text-error/70"><span className="material-symbols-outlined">close</span></button>
  </div>
);

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return "Good morning";
  if (hour >= 12 && hour < 17) return "Good afternoon";
  if (hour >= 17 && hour < 21) return "Good evening";
  return "Good night";
};
