import React from 'react';
import { User, Mail, Phone, ShoppingBag, TrendingUp, Star } from 'lucide-react';

export default function CustomerProfile({ customer }) {
  if (!customer) return null;

  return (
    <div className="bg-[#18191c] border border-[#2a2b2f] rounded-xl p-5 shadow-lg w-full">
      <div className="flex items-center gap-4 mb-5 border-b border-[#2a2b2f] pb-4">
        <div className="w-12 h-12 bg-[#2a2b2f] rounded-full flex items-center justify-center text-gray-400">
          <User size={24} />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">{customer.name}</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-2 py-0.5 rounded font-bold uppercase tracking-wider
              ${customer.tier === 'VIP' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 
              'bg-[#2a2b2f] text-gray-400 border border-gray-600'}`}>
              {customer.tier}
            </span>
            <span className="text-xs text-gray-500 font-mono">ID: {customer.id}</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-3 text-sm text-gray-300">
          <Mail size={16} className="text-gray-500" />
          {customer.email || 'No email on file'}
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-300">
          <Phone size={16} className="text-gray-500" />
          {customer.phone || 'No phone on file'}
        </div>
        
        <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-[#2a2b2f]">
          <div className="bg-[#111214] p-3 rounded-lg border border-[#2a2b2f]">
            <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><ShoppingBag size={12}/> Orders</div>
            <div className="text-xl font-semibold text-white">{customer.order_count}</div>
          </div>
          <div className="bg-[#111214] p-3 rounded-lg border border-[#2a2b2f]">
            <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><TrendingUp size={12}/> LTV</div>
            <div className="text-xl font-semibold text-emerald-400">${customer.lifetime_value}</div>
          </div>
        </div>

        {customer.is_repeat_complaint && (
          <div className="mt-2 bg-red-500/10 border border-red-500/20 text-red-400 text-xs p-2 rounded flex items-center gap-2">
            <Star size={14} /> Repeat Complaint Risk
          </div>
        )}
      </div>
    </div>
  );
}
