import React, { useState, useEffect } from 'react';
import { getWeatherForecast } from '../services/api';

export default function WeatherForecast() {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [permissionDenied, setPermissionDenied] = useState(false);

  useEffect(() => {
    const fetchWeather = async (lat, lon) => {
      try {
        setLoading(true);
        const data = await getWeatherForecast(lat, lon);
        if (data.success) {
          setWeatherData(data);
        } else {
          setError('Failed to load weather data.');
        }
      } catch (err) {
        console.error('Weather API Error:', err);
        setError('Weather service is currently unavailable.');
      } finally {
        setLoading(false);
      }
    };

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          fetchWeather(position.coords.latitude, position.coords.longitude);
        },
        (error) => {
          console.warn("Geolocation denied or error:", error);
          setPermissionDenied(true);
          // Fallback location: New Delhi (major agricultural hub proxy)
          fetchWeather(28.6139, 77.2090);
        },
        { timeout: 10000 }
      );
    } else {
      setPermissionDenied(true);
      fetchWeather(28.6139, 77.2090);
    }
  }, []);

  if (loading) {
    return (
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/30 flex flex-col gap-4 animate-pulse">
        <div className="h-6 w-48 bg-surface-variant rounded"></div>
        <div className="flex gap-3 overflow-x-hidden">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <div key={i} className="min-w-[80px] h-[120px] bg-surface-variant rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error && !weatherData) {
    return (
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-error/20 flex flex-col items-center gap-3 text-center">
        <span className="material-symbols-outlined text-error text-4xl">cloud_off</span>
        <div>
          <p className="text-sm font-bold text-on-surface">Weather service unavailable</p>
          <p className="text-xs text-on-surface-variant">Check your connection or try again later.</p>
        </div>
        <button 
          onClick={() => window.location.reload()} 
          className="px-4 py-2 bg-primary text-white rounded-full text-xs font-bold"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Get icon style classes based on material symbols
  const getIconColor = (iconName) => {
    switch (iconName) {
      case 'sunny': return 'text-orange-400 drop-shadow-[0_0_8px_rgba(251,146,60,0.6)]';
      case 'rainy': return 'text-blue-400 drop-shadow-[0_0_8px_rgba(96,165,250,0.4)]';
      case 'thunderstorm': return 'text-purple-400 drop-shadow-[0_0_8px_rgba(192,132,252,0.4)]';
      case 'cloud': return 'text-slate-400';
      default: return 'text-yellow-400';
    }
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl p-4 sm:p-6 shadow-[0_4px_20px_0_rgba(0,0,0,0.02)] border border-outline-variant/50 flex flex-col gap-5 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute -right-10 -top-10 w-32 h-32 bg-primary/5 rounded-full blur-2xl z-0"></div>
      
      <div className="relative z-10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <h2 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">routine</span>
            7-Day Farm Forecast
          </h2>
          {permissionDenied && (
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1 flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">location_disabled</span>
              Using default location. Enable location for accurate data.
            </p>
          )}
          {weatherData?.is_mock && (
            <div className="mt-2 inline-flex items-center gap-1.5 bg-secondary-container/20 text-secondary px-2 py-0.5 rounded-md border border-secondary/20">
               <span className="material-symbols-outlined text-[14px]">science</span>
               <span className="text-[10px] font-bold uppercase tracking-wider">Demo Mode (Simulated Data)</span>
            </div>
          )}
        </div>
      </div>

      {/* Horizontal Scrollable Weather Cards */}
      <div className="relative z-10 flex gap-3 overflow-x-auto pb-2 snap-x hide-scrollbar scroll-smooth">
        {weatherData?.forecast?.map((day, idx) => (
          <div 
            key={idx} 
            className={`min-w-[85px] sm:min-w-[90px] flex flex-col items-center justify-between p-3 rounded-2xl snap-start border transition-colors ${
              idx === 0 
                ? 'bg-primary-container/30 border-primary/20 shadow-sm' 
                : 'bg-surface border-outline-variant/30 hover:bg-surface-container-low'
            }`}
          >
            <span className={`font-label-md text-label-md mb-2 ${idx === 0 ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
              {idx === 0 ? 'Today' : day.day_name}
            </span>
            
            <span className={`material-symbols-outlined icon-fill text-[36px] my-1 ${getIconColor(day.icon)}`}>
              {day.icon}
            </span>
            
            <div className="flex items-center gap-2 mt-2">
              <span className="font-label-lg text-label-lg text-on-surface">{day.temp_max}°</span>
              <span className="font-label-md text-label-md text-on-surface-variant">{day.temp_min}°</span>
            </div>
          </div>
        ))}
      </div>

      {/* Agricultural Insight Banner */}
      {weatherData?.insights && (
        <div className={`relative z-10 p-4 sm:p-5 rounded-xl flex items-start gap-4 shadow-sm border ${
          weatherData.insights.status === 'optimal' 
            ? 'bg-success-container/50 border-success/30 text-on-success-container' 
            : weatherData.insights.status === 'moderate'
            ? 'bg-secondary-container/50 border-secondary/30 text-on-secondary-container'
            : 'bg-error-container/50 border-error/30 text-on-error-container'
        }`}>
          <div className={`p-2 rounded-full flex-shrink-0 ${
            weatherData.insights.status === 'optimal' ? 'bg-success text-on-success' :
            weatherData.insights.status === 'moderate' ? 'bg-secondary text-on-secondary' :
            'bg-error text-on-error'
          }`}>
            <span className="material-symbols-outlined mt-0.5 icon-fill text-[24px]">
              {weatherData.insights.status === 'optimal' ? 'check_circle' : 
               weatherData.insights.status === 'moderate' ? 'info' : 'warning'}
            </span>
          </div>
          <div className="flex-1">
            <h3 className="font-headline-sm text-headline-sm font-bold mb-1">
              {weatherData.insights.title}
            </h3>
            <p className="font-body-md text-body-md opacity-90 leading-relaxed mb-3">
              {weatherData.insights.message}
            </p>
            <div className="bg-white/40 dark:bg-black/20 p-3 rounded-lg border border-black/5 dark:border-white/5">
              <p className="font-label-md text-label-md flex items-start gap-2">
                <span className="material-symbols-outlined text-[18px] mt-0.5 text-primary">lightbulb</span>
                <span className="opacity-90">{weatherData.insights.actionable}</span>
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Hide Scrollbar Styles */}
      <style dangerouslySetInnerHTML={{__html: `
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}} />
    </div>
  );
}
