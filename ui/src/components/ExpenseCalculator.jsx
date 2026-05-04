import React, { useState, useMemo, useEffect, useCallback } from "react";
import { calculateFarmFinances, validateInputs } from "../utils/farmingCalculations";
import { useDebounce } from "../hooks/useDebounce";

const ExpenseCalculator = ({ aiData, onAnalyze }) => {
  const [calculationMode, setCalculationMode] = useState("profit");
  const [targetProfit, setTargetProfit] = useState(25000);
  
  const [inputs, setInputs] = useState({
    landSize: 1,
    seedCost: 2500,
    fertilizerUrea: 300,
    fertilizerDAP: 1350,
    fertilizerPotash: 1000,
    pesticideCost: 3000,
    laborDays: 15,
    laborRate: 400,
    irrigationCost: 2000,
    machineryCost: 5000,
    landPrepCost: 3000,
    transportCost: 1000,
    miscCost: 500,
    yieldPerAcre: 25,
    marketPrice: 2183,
  });

  // Debounce inputs to prevent excessive re-renders during typing
  const debouncedInputs = useDebounce(inputs, 300);
  const debouncedTargetProfit = useDebounce(targetProfit, 300);

  // Calculate yield penalty based on AI data
  const yieldPenalty = useMemo(() => {
    let penalty = 0;
    if (aiData?.disease) {
      const severity = aiData.disease.severity?.toLowerCase();
      if (severity === "critical") penalty += 0.40;
      else if (severity === "high") penalty += 0.25;
      else if (severity === "moderate") penalty += 0.15;
    }
    const coverage = aiData?.segmentation?.vegetation_percent / 100 || 1.0;
    if (coverage < 0.8) {
      penalty += (0.8 - coverage) * 0.5;
    }
    return Math.min(penalty, 0.7);
  }, [aiData]);

  const effectiveYield = debouncedInputs.yieldPerAcre * (1 - yieldPenalty);

  // Centralized calculations using the engine
  const results = useMemo(() => {
    return calculateFarmFinances(debouncedInputs, effectiveYield, debouncedTargetProfit);
  }, [debouncedInputs, effectiveYield, debouncedTargetProfit]);

  const insights = useMemo(() => {
    const list = [];
    if (yieldPenalty > 0) {
      list.push({
        type: "error",
        text: `AI Detected Health Issues: Yield estimate reduced by ${(yieldPenalty * 100).toFixed(0)}%.`,
        icon: "warning"
      });
    }

    if (calculationMode === "noLossPrice") {
      list.push({
        type: "info",
        text: `To cover all costs, sell at no less than ₹${results.noLossPrice.toFixed(0)}/qtl.`,
        icon: "payments"
      });
    } else if (calculationMode === "reqYield") {
      list.push({
        type: "info",
        text: `Min yield needed: ${results.requiredYieldPerAcre.toFixed(1)} qtl/acre.`,
        icon: "eco"
      });
    }

    const fertPercent = (results.totalFertilizer / results.totalExpense) * 100;
    if (fertPercent > 25) {
      list.push({ type: "warning", text: "Fertilizer cost is high (>25% of budget).", icon: "science" });
    }

    return list;
  }, [results, yieldPenalty, calculationMode]);

  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    const numValue = parseFloat(value);
    setInputs(prev => ({ ...prev, [name]: isNaN(numValue) ? 0 : numValue }));
  }, []);

  return (
    <div className="flex flex-col gap-6 p-1 font-sans animate-fade-in">
      {/* Header & Mode Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-on-surface tracking-tight">Farming Calculator</h2>
          <p className="text-sm text-on-surface-variant font-medium">Standardized Agricultural Insights</p>
        </div>
        
        <div className="flex bg-surface-container-high p-1 rounded-2xl border border-outline-variant/30">
          <ModeTab active={calculationMode === "profit"} onClick={() => setCalculationMode("profit")} label="Profit" icon="trending_up" />
          <ModeTab active={calculationMode === "noLossPrice"} onClick={() => setCalculationMode("noLossPrice")} label="No Loss" icon="balance" />
          <ModeTab active={calculationMode === "reqYield"} onClick={() => setCalculationMode("reqYield")} label="Req Yield" icon="grass" />
          <ModeTab active={calculationMode === "maxBudget"} onClick={() => setCalculationMode("maxBudget")} label="Budget" icon="account_balance" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-5">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-outline-variant/30 p-6 shadow-sm overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
              <span className="material-symbols-outlined text-8xl">calculate</span>
            </div>
            
            <h3 className="text-xs font-black text-primary uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">edit_note</span>
              Configuration
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
              <MemoizedInputGroup label="Land Size (Acres)" name="landSize" value={inputs.landSize} onChange={handleInputChange} icon="area_chart" />
              <MemoizedInputGroup label="Expected Yield (Qtl/Acre)" name="yieldPerAcre" value={inputs.yieldPerAcre} onChange={handleInputChange} icon="shopping_basket" highlight />
              
              <div className="md:col-span-2 grid grid-cols-2 gap-4">
                <MemoizedInputGroup label="Market Price (₹/Qtl)" name="marketPrice" value={inputs.marketPrice} onChange={handleInputChange} icon="payments" highlight />
                {calculationMode === "maxBudget" && (
                   <div className="flex flex-col gap-1.5 animate-slide-in-top">
                      <label className="text-[11px] font-bold uppercase tracking-tight text-primary flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[16px]">target</span> Target Profit (₹)
                      </label>
                      <input type="number" value={targetProfit} onChange={(e) => setTargetProfit(parseFloat(e.target.value) || 0)} className="w-full px-4 py-3 text-sm rounded-xl bg-primary/5 border border-primary/30 focus:outline-none focus:ring-1 focus:ring-primary/20 font-bold" />
                   </div>
                )}
              </div>

              <div className="md:col-span-2 h-px bg-outline-variant/20 my-2" />

              <MemoizedInputGroup label="Seeds (₹/Acre)" name="seedCost" value={inputs.seedCost} onChange={handleInputChange} icon="eco" />
              <MemoizedInputGroup label="Pesticides (₹/Acre)" name="pesticideCost" value={inputs.pesticideCost} onChange={handleInputChange} icon="pest_control" />
              
              <div className="md:col-span-2 grid grid-cols-3 gap-3 p-4 bg-surface-container-low rounded-2xl border border-outline-variant/10">
                <MemoizedInputGroup label="Urea (₹)" name="fertilizerUrea" value={inputs.fertilizerUrea} onChange={handleInputChange} compact />
                <MemoizedInputGroup label="DAP (₹)" name="fertilizerDAP" value={inputs.fertilizerDAP} onChange={handleInputChange} compact />
                <MemoizedInputGroup label="Potash (₹)" name="fertilizerPotash" value={inputs.fertilizerPotash} onChange={handleInputChange} compact />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <MemoizedInputGroup label="Labor Days" name="laborDays" value={inputs.laborDays} onChange={handleInputChange} icon="groups" />
                <MemoizedInputGroup label="Rate (₹/Day)" name="laborRate" value={inputs.laborRate} onChange={handleInputChange} />
              </div>
              <MemoizedInputGroup label="Irrigation (₹)" name="irrigationCost" value={inputs.irrigationCost} onChange={handleInputChange} icon="water" />
              <MemoizedInputGroup label="Machinery (₹)" name="machineryCost" value={inputs.machineryCost} onChange={handleInputChange} icon="agriculture" />
              <MemoizedInputGroup label="Logistics (₹)" name="transportCost" value={inputs.transportCost} onChange={handleInputChange} icon="local_shipping" />
            </div>
          </div>
        </div>

        <div className="lg:col-span-5 flex flex-col gap-5">
          <div className="bg-primary text-white rounded-[2rem] p-8 shadow-xl shadow-primary/20 relative overflow-hidden">
            <div className="absolute -right-8 -bottom-8 opacity-10">
              <span className="material-symbols-outlined text-[160px]">insights</span>
            </div>
            
            <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-70">
              {calculationMode === "profit" ? "Estimated Net Profit" : 
               calculationMode === "noLossPrice" ? "Min Selling Price" :
               calculationMode === "reqYield" ? "Required Yield" : "Max Input Budget"}
            </span>
            
            <div className="mt-2 mb-6">
              <h4 className="text-5xl font-black tracking-tighter">
                {calculationMode === "profit" && `₹${results.netProfit.toLocaleString()}`}
                {calculationMode === "noLossPrice" && `₹${results.noLossPrice.toFixed(0)}`}
                {calculationMode === "reqYield" && `${results.requiredYield.toFixed(1)} Qtl`}
                {calculationMode === "maxBudget" && `₹${results.maxBudgetTotal.toLocaleString()}`}
              </h4>
              <p className="text-sm font-bold opacity-80 mt-1">
                {calculationMode === "profit" ? `${results.profitMargin.toFixed(1)}% margin` :
                 calculationMode === "noLossPrice" ? "per quintal" :
                 calculationMode === "reqYield" ? `or ${results.requiredYieldPerAcre.toFixed(1)} qtl/acre` :
                 `Limit to ₹${results.maxBudgetPerAcre.toLocaleString()}/acre`}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <p className="text-[9px] font-black uppercase tracking-widest opacity-60 mb-1">Total Cost</p>
                <p className="text-lg font-bold">₹{results.totalExpense.toLocaleString()}</p>
              </div>
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <p className="text-[9px] font-black uppercase tracking-widest opacity-60 mb-1">Adj. Yield</p>
                <p className="text-lg font-bold">{results.totalYield.toFixed(1)} Qtl</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-outline-variant/30 p-6 shadow-sm flex flex-col gap-4">
            <h3 className="text-[10px] font-black text-on-surface uppercase tracking-[0.2em] flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-primary">psychology</span>
              Smart Advisories
            </h3>
            
            <div className="space-y-3">
              {insights.map((insight, i) => (
                <div key={i} className={`flex gap-3 items-start p-4 rounded-2xl border transition-all ${getInsightTheme(insight.type)}`}>
                   <span className="material-symbols-outlined text-[20px]">{insight.icon}</span>
                   <p className="text-[11px] leading-relaxed font-bold">{insight.text}</p>
                </div>
              ))}
            </div>

            <button 
              className="mt-2 w-full py-4 bg-surface-container-high rounded-2xl text-xs font-black text-on-surface-variant hover:bg-primary hover:text-white transition-all flex items-center justify-center gap-3 border border-outline-variant/20 shadow-sm"
              onClick={() => {
                const summary = `Total Cost: ₹${results.totalExpense}, Profit: ₹${results.netProfit}, Yield: ${results.totalYield} Qtl, Disease: ${aiData?.disease?.predicted_class || 'None'}`;
                onAnalyze(summary);
              }}
            >
              <span className="material-symbols-outlined text-[20px]">smart_toy</span>
              GET PERSONALIZED SUGGESTIONS
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const ModeTab = React.memo(({ active, onClick, label, icon }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[11px] font-black uppercase tracking-tighter transition-all ${
      active ? 'bg-primary text-white shadow-lg' : 'text-on-surface-variant hover:bg-surface-variant'
    }`}
  >
    <span className="material-symbols-outlined text-[18px]">{icon}</span>
    {label}
  </button>
));

const InputGroup = ({ label, name, value, onChange, icon, compact = false, highlight = false }) => (
  <div className={`flex flex-col gap-1.5 ${compact ? '' : 'mb-1'}`}>
    <label className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant opacity-60 flex items-center gap-1.5">
      {icon && <span className="material-symbols-outlined text-[14px]">{icon}</span>}
      {label}
    </label>
    <input 
      type="number"
      name={name}
      value={value}
      onChange={onChange}
      className={`w-full px-4 ${compact ? 'py-2.5 text-xs' : 'py-3.5 text-sm'} rounded-xl bg-surface border-2 border-outline-variant/30 focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/5 transition-all font-bold ${highlight ? 'bg-primary/5 border-primary/20' : ''}`}
    />
  </div>
);

const MemoizedInputGroup = React.memo(InputGroup);

const getInsightTheme = (type) => {
  switch (type) {
    case "error": return "bg-error/5 border-error/20 text-error";
    case "warning": return "bg-secondary/5 border-secondary/20 text-secondary";
    case "info": return "bg-blue-500/5 border-blue-500/20 text-blue-600";
    default: return "bg-surface-container border-outline-variant/10 text-on-surface-variant";
  }
};

export default ExpenseCalculator;
