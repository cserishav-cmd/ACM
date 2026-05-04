import React, { useRef } from "react";
import Logo from "./Logo";
import MarkdownRenderer from "./MarkdownRenderer";

export default function Result({ data, file, onReset, onMarket }) {
  if (!data) return null;
  const { segmentation, disease, variety, decision, health_report, input_gate, analysis_scope, ai_insight } = data;
  const report = decision || health_report;
  const isHealthOnly = analysis_scope === "health_only";
  const confidenceText = Number.isFinite(disease?.confidence)
    ? `${(disease.confidence * 100).toFixed(1)}%`
    : "N/A";

  const isHealthy = disease?.is_healthy;
  const severityClass = disease?.severity === "none" ? "none" : disease?.severity === "critical" ? "critical" : disease?.severity === "high" ? "high" : "moderate";

  const getRiskColor = () => {
    if (isHealthy) return "bg-success-container text-success";
    if (severityClass === "critical" || severityClass === "high") return "bg-error-container text-on-error-container border-error/20";
    return "bg-secondary-container text-on-secondary-container border-secondary/20";
  };

  const getRiskText = () => {
    if (isHealthy) return "Healthy";
    if (severityClass === "critical") return "Critical Risk Identified";
    if (severityClass === "high") return "High Risk Identified";
    return "Moderate Risk Identified";
  };

  const getRiskIcon = () => {
    if (isHealthy) return "check_circle";
    return "warning";
  };

  const isGrainOnly = analysis_scope === "grain_analysis";

  const [imagePreview, setImagePreview] = React.useState(null);
  React.useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setImagePreview(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  const [chatMessages, setChatMessages] = React.useState([]);
  const [isChatLoading, setIsChatLoading] = React.useState(false);
  const [showMask, setShowMask] = React.useState(true);
  const chatEndRef = useRef(null);

  // Auto-scroll chat
  React.useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isChatLoading]);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message
    const newMessages = [...chatMessages, { role: 'user', text }];
    setChatMessages(newMessages);
    setIsChatLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || '/api'}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          pipeline_results: data
        })
      });

      const result = await response.json();
      if (result.success && result.data && result.data.reply) {
        setChatMessages(prev => [...prev, { role: 'ai', text: result.data.reply }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'ai', text: "Sorry, I couldn't process that right now." }]);
      }
    } catch (error) {
      console.error("Chat API error:", error);
      setChatMessages(prev => [...prev, { role: 'ai', text: "Connection error. Please try again later." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  React.useEffect(() => {
    if (chatMessages.length === 0) {
      setChatMessages([
        { role: 'ai', text: `Hi! I see you uploaded an image of ${variety?.predicted_class || "rice grains"}. What would you like to know about it?` }
      ]);
    }
  }, [chatMessages.length, variety?.predicted_class]);

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden font-sans selection:bg-primary/10">
      {/* 1. Header (Sticky) */}
      <header className="h-14 shrink-0 bg-surface border-b border-outline-variant/30 px-6 flex items-center justify-between z-50">
        <div className="flex items-center gap-6">
          <div
            className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity active:scale-95"
            onClick={onReset}
            title="Reset Scan"
          >
            <Logo className="h-9" />
          </div>
          <div className="hidden lg:flex items-center gap-4 border-l border-outline-variant/30 pl-4">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-surface-container rounded-full border border-outline-variant/30">
              <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">{isHealthy ? 'System Health: Optimal' : 'Action Required'}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button onClick={onReset} className="flex items-center gap-2 px-3 py-1.5 hover:bg-surface-variant rounded-lg transition-all text-on-surface-variant border border-transparent hover:border-outline-variant/30">
            <span className="material-symbols-outlined text-[30px]">refresh</span>
            <span className="text-xs font-bold">New Scan</span>
          </button>
          <div className="w-8 h-8 roundedll bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-xs border border-primary/10">TESTING</div>
        </div>
      </header>

      {/* 2. Metrics Bar (Sub-header) - Hidden for Grain Only */}
      {!isGrainOnly && (
        <div className="h-11 shrink-0 bg-surface-container-lowest border-b border-outline-variant/20 px-6 flex items-center gap-6 overflow-x-auto no-scrollbar scroll-smooth">
          <div className="flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-primary text-[18px] icon-fill">potted_plant</span>
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">Diagnosis: <span className="text-on-surface ml-1">{disease?.predicted_class}</span></span>
          </div>
          <div className="w-px h-4 bg-outline-variant/30"></div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-secondary text-[18px] icon-fill">analytics</span>
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">Conf: <span className="text-on-surface ml-1">{confidenceText}</span></span>
          </div>
          <div className="w-px h-4 bg-outline-variant/30"></div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-tertiary text-[18px] icon-fill">vital_signs</span>
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">Health Score: <span className="text-on-surface ml-1">{report?.health_score || 0}%</span></span>
          </div>
          <div className="w-px h-4 bg-outline-variant/30"></div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-error text-[18px] icon-fill">warning</span>
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">Severity: <span className="text-error ml-1">{severityClass}</span></span>
          </div>
        </div>
      )}

      <div className="flex-grow flex overflow-hidden">
        {/* 3. Left Sidebar (Fixed) - Hidden for Grain Only */}
        {!isGrainOnly && (
          <aside className="hidden md:flex flex-col w-16 shrink-0 bg-surface border-r border-outline-variant/30 items-center py-6 gap-8 z-40">
            <button className="w-10 h-10 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center transition-all hover:scale-110 shadow-sm">
              <span className="material-symbols-outlined icon-fill">dashboard</span>
            </button>
            <button className="w-10 h-10 rounded-xl text-on-surface-variant flex items-center justify-center hover:bg-surface-variant transition-all">
              <span className="material-symbols-outlined">groups</span>
            </button>
            <button
              onClick={onMarket}
              className="w-10 h-10 rounded-xl text-on-surface-variant flex items-center justify-center hover:bg-surface-variant transition-all"
            >
              <span className="material-symbols-outlined">storefront</span>
            </button>
            <div className="mt-auto">
              <button className="w-10 h-10 rounded-xl text-on-surface-variant flex items-center justify-center hover:bg-surface-variant transition-all">
                <span className="material-symbols-outlined">settings</span>
              </button>
            </div>
          </aside>
        )}

        {/* 4. Main Dashboard Area */}
        <div className="flex-grow flex flex-col lg:flex-row overflow-hidden bg-surface-container-low/30">

          {/* Analysis Dashboard (Left/Center) */}
          <div className={`flex-grow overflow-y-auto no-scrollbar p-5 ${isGrainOnly ? 'flex items-center justify-center' : ''}`}>
            <div className={`w-full max-w-5xl mx-auto flex flex-col gap-5 ${isGrainOnly ? 'max-w-2xl' : ''}`}>

              {/* Compact Diagnostics Header */}
              <div className={`flex flex-col md:flex-row gap-5 ${isGrainOnly ? 'md:flex-col' : ''}`}>
                {/* Hero Card */}
                <section className={`${isGrainOnly ? 'w-full' : 'md:w-5/12'} bg-surface-container-lowest rounded-2xl overflow-hidden border border-outline-variant/40 shadow-sm flex flex-col shrink-0`}>
                  <div className={`${isGrainOnly ? 'h-auto max-h-[500px]' : 'h-80'} w-full bg-surface-container relative group flex items-center justify-center`}>
                    {/* Real Image Base */}
                    {imagePreview ? (
                      <img 
                        src={imagePreview} 
                        alt="Original" 
                        className={`w-full ${isGrainOnly ? 'h-auto object-contain max-h-[500px]' : 'h-full object-cover absolute inset-0'}`} 
                      />
                    ) : (
                      <div className="w-full h-80 flex items-center justify-center bg-surface-container-high absolute inset-0"><span className="material-symbols-outlined text-4xl opacity-20">landscape</span></div>
                    )}

                    {/* AI Mask Overlay (Paddy Only) */}
                    {!isGrainOnly && segmentation?.mask_base64 && (
                      <img
                        src={`data:image/png;base64,${segmentation.mask_base64}`}
                        alt="Mask"
                        className={`w-full h-full object-cover absolute inset-0 mix-blend-multiply transition-opacity duration-500 z-20 ${showMask ? 'opacity-80' : 'opacity-0'}`}
                      />
                    )}

                    {/* Mask Toggle Button (Paddy Only) */}
                    {!isGrainOnly && segmentation?.mask_base64 && (
                      <button
                        onClick={(e) => { e.stopPropagation(); setShowMask(!showMask); }}
                        className="absolute bottom-3 right-3 z-40 bg-white/90 backdrop-blur-md text-primary text-[10px] font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 shadow-lg border border-primary/20 hover:bg-primary hover:text-white transition-all active:scale-95"
                      >
                        <span className="material-symbols-outlined text-[14px]">{showMask ? 'layers_clear' : 'layers'}</span>
                        {showMask ? 'VIEW ORIGINAL' : 'SHOW AI ANALYSIS'}
                      </button>
                    )}
                  </div>
                  <div className="p-4 flex flex-col">
                    <div className="flex items-center justify-between">
                      <h1 className="text-headline-sm font-bold text-on-surface leading-tight truncate">
                        {isGrainOnly ? variety?.predicted_class : disease?.predicted_class}
                      </h1>
                      {isGrainOnly && variety?.confidence && (
                         <span className="text-[10px] font-black bg-primary/10 text-primary px-2.5 py-1 rounded-full uppercase tracking-tighter">
                            { (variety.confidence * 100).toFixed(1) }% Match
                         </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] font-bold text-primary uppercase tracking-widest">{isGrainOnly ? 'Variety Detected' : 'Condition Diagnosed'}</span>
                    </div>
                  </div>
                </section>

                {/* Attributes / Details Card */}
                <section className={`flex-grow bg-surface-container-lowest border border-outline-variant/40 rounded-2xl p-5 shadow-sm flex flex-col overflow-hidden ${isGrainOnly ? 'h-auto' : 'h-[360px] md:h-auto'}`}>
                  <div className="flex items-center justify-between mb-3 shrink-0">
                    <h3 className="text-title-sm font-bold flex items-center gap-2 text-on-surface">
                      <span className="material-symbols-outlined text-primary text-[20px]">{isGrainOnly ? 'info' : 'list_alt'}</span>
                      {isGrainOnly ? 'Rice Variety Attributes' : 'Recommendation Summary'}
                    </h3>
                  </div>
                  <div className="overflow-y-auto no-scrollbar flex-grow space-y-3">
                    <p className={`text-sm text-on-surface-variant leading-relaxed ${isGrainOnly ? 'text-base font-medium text-on-surface' : ''}`}>
                      {variety?.description || disease?.recommendation || "Finalizing report..."}
                    </p>
                    
                    {/* Only for Paddy: List recommendations */}
                    {!isGrainOnly && report?.recommendations?.map((rec, i) => (
                      <div key={i} className="flex gap-3 p-3 rounded-xl bg-surface border border-outline-variant/20 hover:border-primary/30 transition-colors">
                        <span className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 font-bold text-[10px]">{i + 1}</span>
                        <span className="text-[13px] text-on-surface-variant leading-snug">{rec}</span>
                      </div>
                    ))}

                    {/* Only for Grain: Attributes Table/List */}
                    {isGrainOnly && (
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="p-4 bg-primary/5 rounded-2xl border border-primary/10">
                           <p className="text-[9px] font-black uppercase tracking-widest text-primary/60 mb-1">Origin</p>
                           <p className="text-xs font-bold text-on-surface">West Bengal Heritage</p>
                        </div>
                        <div className="p-4 bg-secondary/5 rounded-2xl border border-secondary/10">
                           <p className="text-[9px] font-black uppercase tracking-widest text-secondary/60 mb-1">Market Category</p>
                           <p className="text-xs font-bold text-on-surface">{variety?.predicted_class?.includes('Polao') ? 'Fine Aromatic' : 'Premium Grain'}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </section>
              </div>

              {/* Paddy-Only Sections: Risk Alert, Yield, Pesticide, Soil Advisor */}
              {!isGrainOnly && (
                <>
                  {/* Highlight Section: Critical Pest/Disease Alert */}
                  {!isHealthy && (
                    <div className="mb-5 p-1 rounded-3xl bg-gradient-to-r from-error/40 via-primary/20 to-error/40 animate-pulse-slow">
                      <div className="bg-surface-container-lowest rounded-[22px] p-5 flex flex-col md:flex-row items-center justify-between gap-4 border border-error/10">
                        <div className="flex items-center gap-4 text-center md:text-left">
                          <div className="w-14 h-14 rounded-2xl bg-error/10 flex items-center justify-center shrink-0">
                            <span className="material-symbols-outlined text-error text-[32px] icon-fill">report_problem</span>
                          </div>
                          <div>
                            <h4 className="text-title-md font-black text-on-surface tracking-tight">ACTION REQUIRED: {disease?.predicted_class?.toUpperCase()} DETECTED</h4>
                            <p className="text-[12px] text-on-surface-variant leading-relaxed max-w-lg">
                              Our AI has confirmed <span className="font-bold text-error">{disease?.predicted_class}</span> damage in your crop. Immediate intervention with authorized insecticides is recommended to prevent up to <span className="font-bold">40% yield loss</span>.
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={onMarket}
                          className="bg-primary text-on-primary font-black text-[12px] px-8 py-4 rounded-2xl flex items-center gap-2 shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-all whitespace-nowrap"
                        >
                          <span className="material-symbols-outlined text-[20px]">shopping_cart</span>
                          GO TO MARKETPLACE
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-4 flex-grow">
                    <div className="flex flex-col gap-5">
                      {/* Yield Insights Card */}
                      <section className="bg-surface-container-lowest border border-outline-variant/40 rounded-2xl p-5 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-title-sm font-bold flex items-center gap-2">
                            <span className="material-symbols-outlined text-secondary text-[20px]">monitoring</span>
                            Yield Outlook
                          </h3>
                          <span className="text-[11px] font-bold text-secondary uppercase bg-secondary/10 px-2 py-0.5 rounded-full">{isHealthy ? 'Strong' : 'At Risk'}</span>
                        </div>
                        <div className="flex flex-col gap-4">
                          <div className="flex items-end justify-between">
                            <div className="flex flex-col">
                              <span className="text-headline-md font-bold text-on-surface leading-none">{report?.health_score || 0}%</span>
                              <span className="text-[10px] font-bold text-on-surface-variant opacity-60 uppercase tracking-widest mt-1">Projected Health</span>
                            </div>
                            <div className="w-32 h-2 bg-surface-variant rounded-full overflow-hidden mb-2">
                              <div className="h-full bg-secondary transition-all duration-1000" style={{ width: `${report?.health_score || 0}%` }}></div>
                            </div>
                          </div>
                          <div className="p-3 bg-secondary/5 rounded-xl border border-secondary/10">
                            <div className="flex items-center gap-2 text-[11px] text-secondary font-bold">
                              <span className="material-symbols-outlined text-[16px]">info</span>
                              Yield reduction estimated at {100 - (report?.health_score || 0)}% if untreated.
                            </div>
                          </div>
                        </div>
                      </section>

                      {/* Pesticide Card */}
                      <section className="bg-surface-container-lowest border border-outline-variant/40 rounded-2xl p-5 shadow-sm flex flex-col flex-grow">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-title-sm font-bold flex items-center gap-2">
                            <span className="material-symbols-outlined text-error text-[20px]">science</span>
                            Pesticide Strategy
                          </h3>
                          <span className="text-[9px] font-bold text-on-surface-variant/40 uppercase tracking-widest">Chemical Control</span>
                        </div>
                        <div className={`p-4 rounded-xl border ${isHealthy ? 'bg-success/5 border-success/20' : 'bg-error/5 border-error/20'}`}>
                          <div className="flex items-start gap-3">
                            <span className={`material-symbols-outlined ${isHealthy ? 'text-success' : 'text-error'} text-[20px]`}>
                              {isHealthy ? 'check_circle' : 'warning_amber'}
                            </span>
                            <div className="flex flex-col gap-1">
                              <p className="text-[13px] font-bold text-on-surface">
                                {isHealthy ? "No Pesticides Needed" : `Targeted: ${disease?.predicted_class}`}
                              </p>
                              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                                {isHealthy
                                  ? "Your crop is healthy. Focus on balanced nutrition (N-P-K) and regular monitoring to maintain immunity."
                                  : disease?.predicted_class === "Tungro" ? "Apply Imidacloprid (0.5ml/L) or Thiamethoxam (0.5g/L) to control Green Leafhopper vectors."
                                    : disease?.predicted_class === "Blast" ? "Apply Tricyclazole 75 WP (0.6g/L) or Carbendazim (1g/L) immediately."
                                      : disease?.predicted_class === "Brown Spot" ? "Spray Mancozeb (2g/L) or Propiconazole (1ml/L) to manage fungal spread."
                                        : disease?.predicted_class === "Dead Heart" || disease?.predicted_class === "White Head" ? "Stem Borer detected. Apply Carbofuran 3G (25kg/ha) or Chlorantraniliprole 0.4G (10kg/ha)."
                                          : disease?.predicted_class === "Leaf Folder" ? "Apply Flubendiamide 39.35 SC (50ml/ha) or Chlorantraniliprole 18.5 SC (150ml/ha)."
                                            : disease?.predicted_class === "Brown Plant Hopper" ? "Apply Pymetrozine 50 WG (300g/ha) or Dinotefuran 20 SG (200g/ha)."
                                              : "Consult Krishi Vigyan Kendra (KVK) for specific chemical dosage."
                                }
                              </p>
                            </div>
                          </div>
                        </div>
                      </section>
                    </div>

                    {/* AI Soil Card */}
                    <section className="bg-surface-container-lowest border border-outline-variant/40 rounded-2xl p-5 shadow-sm flex flex-col h-full">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="material-symbols-outlined text-tertiary text-[20px]">psychology</span>
                        <h3 className="text-title-sm font-bold">AI Soil Advisor</h3>
                      </div>
                      <div className="flex-grow bg-tertiary/5 rounded-xl p-4 overflow-y-auto no-scrollbar text-xs text-on-surface-variant leading-relaxed">
                        <MarkdownRenderer content={ai_insight || "Analyzing soil parameters..."} animate={true} />
                      </div>
                    </section>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* 5. Right Chatbot (Fixed Width) */}
          <aside className={`${isGrainOnly ? 'w-full lg:w-[400px]' : 'w-full lg:w-[320px] xl:w-[380px]'} shrink-0 bg-surface border-l border-outline-variant/30 flex flex-col overflow-hidden shadow-[-4px_0_15px_rgba(0,0,0,0.02)]`}>
            <div className="h-14 border-b border-outline-variant/30 px-5 flex items-center justify-between shrink-0 bg-surface/50 backdrop-blur-md">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(var(--primary-rgb),0.5)]"></div>
                <h2 className="text-title-sm font-bold text-primary tracking-tight">{isGrainOnly ? "Variety Assistant" : "CropCare AI"}</h2>
              </div>
              <div className="flex items-center gap-1.5 bg-green-100 text-green-700 px-2 py-1 rounded-md">
                <span className="text-[9px] font-black uppercase tracking-tighter">Live Support</span>
              </div>
            </div>

            {/* Chat Body */}
            <div className="flex-grow overflow-y-auto p-5 space-y-5 no-scrollbar bg-gradient-to-b from-surface-container-lowest/10 to-transparent">
              {chatMessages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4 opacity-40">
                  <div className="w-16 h-16 rounded-3xl bg-primary/10 flex items-center justify-center">
                    <span className="material-symbols-outlined text-3xl text-primary">forum</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-on-surface">Assistant Ready</h4>
                    <p className="text-[11px] mt-1">Ask anything about fertilizers, crop spacing, or this {isGrainOnly ? "variety" : "diagnosis"}.</p>
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, i) => (
                  <div key={i} className={`flex flex-col ${msg.role === 'ai' ? 'items-start' : 'items-end'}`}>
                    <div className={`p-3.5 rounded-2xl max-w-[90%] text-[13px] leading-relaxed shadow-sm ${msg.role === 'ai'
                      ? 'bg-surface-container-low text-on-surface border border-outline-variant/30 rounded-tl-sm'
                      : 'bg-primary text-on-primary rounded-tr-sm'
                      }`}>
                      <MarkdownRenderer content={msg.text} animate={msg.role === 'ai' && i === chatMessages.length - 1} />
                    </div>
                    <span className="text-[9px] mt-1 opacity-30 px-1">{msg.role === 'ai' ? 'Assistant' : 'You'}</span>
                  </div>
                ))
              )}
              <div ref={chatEndRef} />
              {isChatLoading && (
                <div className="self-start flex gap-1 p-2">
                  <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-outline-variant/30 bg-surface shrink-0">
              <div className="relative group">
                <input
                  type="text"
                  placeholder={`Ask about this ${isGrainOnly ? "rice variety" : "diagnosis"}...`}
                  className="w-full pl-4 pr-12 py-3.5 rounded-2xl bg-surface-container-low border border-outline-variant/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 text-sm transition-all shadow-inner"
                  disabled={isChatLoading}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.target.value.trim() && !isChatLoading) {
                      const val = e.target.value.trim();
                      e.target.value = '';
                      handleSendMessage(val);
                    }
                  }}
                />
                <button
                  className="absolute right-2 top-2 w-10 h-10 bg-primary text-on-primary rounded-xl flex items-center justify-center shadow-lg hover:brightness-110 active:scale-95 transition-all"
                  onClick={(e) => {
                    const input = e.currentTarget.previousElementSibling;
                    if (input.value.trim() && !isChatLoading) {
                      const val = input.value.trim();
                      input.value = '';
                      handleSendMessage(val);
                    }
                  }}
                >
                  <span className="material-symbols-outlined text-[18px]">send</span>
                </button>
              </div>
              <p className="text-[10px] text-center mt-3 text-on-surface-variant opacity-40">Powered by CropCare NVIDIA NIM Advisor</p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
