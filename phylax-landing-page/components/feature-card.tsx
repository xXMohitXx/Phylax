import React from 'react';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  variant?: 'default' | 'glow';
}

export function FeatureCard({ title, description, icon: Icon, variant = 'default' }: FeatureCardProps) {
  return (
    <div className={`relative group p-6 rounded-2xl border transition-all duration-300 ${
      variant === 'glow' 
        ? 'border-black/10 bg-porcelain hover:bg-white hover:border-black/20 hover:shadow-[0_8px_30px_rgba(38,28,21,0.08)]' 
        : 'border-black/5 bg-porcelain/80 hover:bg-porcelain hover:border-black/10'
    }`}>
      {variant === 'glow' && (
        <div className="absolute inset-0 bg-gradient-to-br from-beige/30 to-porcelain/30 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl pointer-events-none" />
      )}
      
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-6 transition-colors ${
        variant === 'glow'
          ? 'bg-lime-cream/20 text-lime-cream group-hover:bg-lime-cream/40 group-hover:text-coffee-bean'
          : 'bg-beige text-lime-cream group-hover:text-coffee-bean'
      }`}>
        <Icon className="w-6 h-6" />
      </div>
      
      <h3 className="text-xl font-bold text-coffee-bean mb-2 tracking-tight">{title}</h3>
      <p className="text-coffee-bean/80 leading-relaxed text-sm">
        {description}
      </p>
    </div>
  );
}
