import React from "react";
import katyayaniDemat from "../assets/Katyayani Demat Insecticide For Paddy 1 L .png";
import nagarjunaProfex from "../assets/Nagarjuna Profex Super Insecticide.png";
import paddyKit from "../assets/KATYAYANI PADDY INSECT CONTROL KIT.png";

const products = [
  {
    id: 1,
    name: "Katyayani Demat Insecticide",
    subtitle: "Systemic Control for Paddy",
    price: "₹850.00",
    image: katyayaniDemat,
    tag: "Best Seller",
    color: "bg-blue-500",
    description: "Highly effective systemic insecticide for controlling sucking pests and stem borers in paddy crops."
  },
  {
    id: 2,
    name: "Nagarjuna Profex Super",
    subtitle: "Broad Spectrum Protection",
    price: "₹1,200.00",
    image: nagarjunaProfex,
    tag: "High Potency",
    color: "bg-red-500",
    description: "Combination insecticide (Profenofos + Cypermethrin) for immediate knockdown effect against bollworms and leaf folders."
  },
  {
    id: 3,
    name: "Paddy Insect Control Kit",
    subtitle: "Complete Seasonal Protection",
    price: "₹2,499.00",
    image: paddyKit,
    tag: "Full Kit",
    color: "bg-green-600",
    description: "A complete curated kit containing insecticides, growth promoters, and stickers for full-season paddy protection."
  }
];

export default function OrderPage({ onBack }) {
  const [cart, setCart] = React.useState([]);

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-32 selection:bg-primary/10">
      {/* Header */}
      <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between sticky top-0 z-50 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="w-10 h-10 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors group">
            <span className="material-symbols-outlined text-slate-600 dark:text-slate-400 group-hover:text-primary">arrow_back</span>
          </button>
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100">CropCare Market</h1>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-widest font-bold">Authorized Pesticides & Tools</p>
          </div>
        </div>
        
        <div className="relative">
          <button className="w-12 h-12 bg-primary/10 text-primary rounded-xl flex items-center justify-center hover:bg-primary hover:text-white transition-all shadow-sm">
            <span className="material-symbols-outlined">shopping_cart</span>
          </button>
          {cart.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-white animate-bounce">
              {cart.length}
            </span>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-6 flex flex-col gap-8">
        {/* Banner */}
        <div className="bg-gradient-to-r from-primary to-green-700 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl shadow-primary/20">
          <div className="relative z-10 flex flex-col gap-2 max-w-md">
            <span className="text-[10px] font-bold uppercase tracking-widest bg-white/20 px-2 py-1 rounded-md w-fit">Seasonal Offer</span>
            <h2 className="text-3xl font-bold">Protect Your Yield Today</h2>
            <p className="text-white/80 text-sm leading-relaxed">Get authentic insecticides delivered directly to your farm. Guaranteed quality from authorized distributors.</p>
            <button className="mt-4 bg-white text-primary font-bold px-6 py-3 rounded-xl w-fit shadow-lg hover:scale-105 transition-transform active:scale-95">Shop All Products</button>
          </div>
          <div className="absolute right-0 top-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-4 flex flex-col gap-4 shadow-sm hover:shadow-xl transition-all group overflow-hidden">
               {/* Image Frame */}
               <div className="bg-slate-50 dark:bg-slate-800 rounded-2xl aspect-square relative flex items-center justify-center p-6 overflow-hidden">
                  <img 
                    src={product.image} 
                    alt={product.name} 
                    className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-500" 
                  />
                  <span className={`absolute top-3 left-3 ${product.color} text-white text-[9px] font-black uppercase px-2 py-1 rounded-md shadow-md`}>
                    {product.tag}
                  </span>
               </div>

               {/* Info */}
               <div className="flex flex-col gap-1 px-1">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-slate-900 dark:text-slate-100 leading-tight">{product.name}</h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">{product.subtitle}</p>
                    </div>
                    <span className="text-primary font-black text-sm">{product.price}</span>
                  </div>
                  <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-2 line-clamp-2 italic">{product.description}</p>
               </div>

               {/* Actions */}
               <div className="flex gap-2 mt-auto">
                  <button className="flex-grow bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-bold py-3 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-xs">Details</button>
                  <button 
                    onClick={() => addToCart(product)}
                    className="w-12 h-12 bg-primary text-white rounded-xl flex items-center justify-center hover:brightness-110 transition-all active:scale-95 shadow-md shadow-primary/20"
                  >
                    <span className="material-symbols-outlined">add_shopping_cart</span>
                  </button>
               </div>
            </div>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
           <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-center">
              <span className="material-symbols-outlined text-primary">verified</span>
              <span className="text-[10px] font-bold uppercase tracking-tight">100% Original</span>
           </div>
           <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-center">
              <span className="material-symbols-outlined text-primary">local_shipping</span>
              <span className="text-[10px] font-bold uppercase tracking-tight">Farm Delivery</span>
           </div>
           <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-center">
              <span className="material-symbols-outlined text-primary">payments</span>
              <span className="text-[10px] font-bold uppercase tracking-tight">Pay on Delivery</span>
           </div>
           <div className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-center">
              <span className="material-symbols-outlined text-primary">support_agent</span>
              <span className="text-[10px] font-bold uppercase tracking-tight">Expert Support</span>
           </div>
        </div>
      </main>
    </div>
  );
}
