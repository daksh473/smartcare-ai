import React from 'react';
import { 
  Brain, 
  Workflow, 
  MessageSquare, 
  Database, 
  Headset, 
  Ticket, 
  BarChart3, 
  Users, 
  TrendingUp, 
  FileSpreadsheet 
} from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: <Brain size={24} />,
      name: "Real-Time Sentiment Analysis",
      desc: "Every customer message is scored instantly from 0 to 1. Detect anger, frustration, or gratitude in milliseconds powered by LLaMA 3.3."
    },
    {
      icon: <Workflow size={24} />,
      name: "Automatic Action Routing",
      desc: "No manual triage. The AI automatically decides whether to escalate to a human, resolve normally, or trigger a predictive upsell."
    },
    {
      icon: <MessageSquare size={24} />,
      name: "Context-Aware AI Replies",
      desc: "Zero generic scripts. Replies are generated fresh based on the customer's mood and language (English, Hindi, or Hinglish)."
    },
    {
      icon: <Database size={24} />,
      name: "Persistent Conversation Memory",
      desc: "Customers never repeat themselves. The system recalls past issues, names, and preferences seamlessly across all future sessions."
    },
    {
      icon: <Headset size={24} />,
      name: "Omnichannel Intelligence",
      desc: "Native support for Live Chat, Email, and Voice. Transcribes spoken audio and replies with text-to-speech in real time."
    },
    {
      icon: <Ticket size={24} />,
      name: "Smart Auto-Ticketing",
      desc: "High-frustration messages instantly generate trackable, prioritized tickets without any manual data entry."
    },
    {
      icon: <BarChart3 size={24} />,
      name: "Live Analytics Dashboard",
      desc: "Visual oversight of your entire operation. Track live escalation rates, 7-day sentiment trends, and an overall Customer Health Score."
    },
    {
      icon: <Users size={24} />,
      name: "Integrated Support CRM",
      desc: "Automatically builds customer profiles from chat histories. Tracks deal pipelines and assigns AI-generated churn risk scores."
    },
    {
      icon: <TrendingUp size={24} />,
      name: "Predictive Forecasting",
      desc: "Stop reacting. The AI predicts churn risks before they happen, surfaces upsell windows, and forecasts your 30-day ticket volume."
    },
    {
      icon: <FileSpreadsheet size={24} />,
      name: "Seamless Excel Integration",
      desc: "Full two-way spreadsheet support. Import legacy lists instantly or export rich, multi-sheet analytics reports with one click."
    }
  ];

  return (
    <section className="py-24 px-6 max-w-[1400px] mx-auto bg-[#f9fafb]">
      <div className="text-center max-w-3xl mx-auto mb-20">
        <h2 className="font-display text-[42px] font-semibold tracking-tight text-[#0a1b33] mb-4">
          Everything you need to understand your customers.
        </h2>
        <p className="text-[17px] leading-relaxed text-slate-500">
          A complete, end-to-end intelligence engine built to eliminate blind spots, stop churn, and automate routine support.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, idx) => (
          <div 
            key={idx} 
            className="group flex flex-col items-start bg-white border border-slate-200/60 rounded-[24px] p-8 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1 hover:border-blue-200"
          >
            <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 mb-6 transition-colors group-hover:bg-blue-100">
              {feature.icon}
            </div>
            <h3 className="font-sans text-xl font-semibold text-[#0a1b33] mb-3 tracking-tight">
              {feature.name}
            </h3>
            <p className="text-[15px] leading-relaxed text-slate-500">
              {feature.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
