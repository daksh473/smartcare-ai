import React from 'react';
import Hero from './Hero';
import Features from './Features';

export default function LandingPage({ onStart }) {
  return (
    <div className="w-full min-h-screen bg-[#f9fafb] pb-24">
      <Hero onStart={onStart} />
      {/* 
        We retain the Features section underneath to preserve 
        the SentimentAI content as requested.
      */}
      <Features />
    </div>
  );
}
