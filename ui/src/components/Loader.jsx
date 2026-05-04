import { useState, useEffect } from "react";

const STEPS = ["Segmenting", "Detecting", "Classifying"];

export default function Loader({ message = "Analyzing your crop..." }) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background pb-32" id="loader">
      <div className="relative w-16 h-16 mb-8">
        <div className="absolute inset-0 border-4 border-outline-variant rounded-full border-t-primary-container animate-spin"></div>
        <div className="absolute inset-2 border-2 border-transparent border-b-primary-fixed-dim rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
      </div>
      
      <p className="text-on-surface-variant font-medium text-lg mb-6">{message}</p>
      
      <div className="flex items-center gap-2 text-sm text-outline">
        {STEPS.map((step, i) => (
          <span key={step} className="flex items-center">
            {i > 0 && <span className="opacity-40 mx-1">→</span>}
            <span className={`px-2 py-1 rounded-full transition-colors duration-300 ${
              i < activeStep ? "text-primary-fixed-dim" : 
              i === activeStep ? "text-primary-container font-semibold bg-primary-container/10" : ""
            }`}>
              {step}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
