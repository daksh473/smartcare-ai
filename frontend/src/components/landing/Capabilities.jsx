import React from 'react';
import { motion } from 'framer-motion';
import FadingVideo from './FadingVideo';
import { ImageIcon, MovieIcon, LightbulbIcon } from './Icons';

export default function Capabilities() {
  const commonMotion = {
    initial: { filter: 'blur(10px)', opacity: 0, y: 20 },
    whileInView: { filter: 'blur(0px)', opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.1 },
    transition: { duration: 0.8, ease: "easeOut" }
  };

  const cards = [
    {
      title: "Design",
      icon: <ImageIcon className="w-5 h-5 text-white" />,
      tags: ["Brand Systems", "Art Direction", "Visual Identity", "Motion"],
      body: "We shape identities and interfaces that feel unmistakably yours — typographic systems, component libraries, and art-directed pages that scale without losing soul."
    },
    {
      title: "Engineering",
      icon: <MovieIcon className="w-5 h-5 text-white" />,
      tags: ["React", "Next.js", "Headless CMS", "Edge-Ready"],
      body: "Production-grade front-ends built on modern stacks. Performant, accessible, and instrumented — with code your team will enjoy extending long after launch."
    },
    {
      title: "Growth",
      icon: <LightbulbIcon className="w-5 h-5 text-white" />,
      tags: ["SEO", "Analytics", "A/B Testing", "Retention"],
      body: "Launch is the starting line. We partner with your team on conversion, content, and iteration loops that turn a beautiful site into a compounding asset."
    }
  ];

  return (
    <section className="min-h-screen overflow-hidden bg-black relative flex flex-col">
      <FadingVideo 
        src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_093722_ccfc7ebf-182f-419f-8a62-2dc02db7dd9d.mp4"
        className="absolute inset-0 w-full h-full object-cover z-0"
      />
      
      <div className="relative z-10 px-8 md:px-16 lg:px-20 pt-24 pb-10 flex flex-col min-h-screen">
        <motion.div {...commonMotion} className="mb-auto">
          <p className="text-sm font-body text-white/80 mb-6 uppercase tracking-widest">// Capabilities</p>
          <h2 className="font-heading italic text-6xl md:text-7xl lg:text-[6rem] leading-[0.9] tracking-[-3px] text-white">
            Studio craft,<br />end to end
          </h2>
        </motion.div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 pb-12">
          {cards.map((card, idx) => (
            <motion.div 
              key={card.title}
              {...commonMotion}
              transition={{ ...commonMotion.transition, delay: 0.2 + (idx * 0.15) }}
              className="liquid-glass rounded-[1.25rem] p-6 min-h-[360px] flex flex-col"
            >
              <div className="flex items-start justify-between">
                <div className="liquid-glass h-11 w-11 rounded-[0.75rem] flex items-center justify-center shrink-0">
                  {card.icon}
                </div>
                <div className="flex flex-wrap justify-end gap-1.5 ml-4">
                  {card.tags.map(tag => (
                    <span key={tag} className="liquid-glass rounded-full px-3 py-1 text-[11px] text-white/90 font-body whitespace-nowrap">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="flex-1"></div>
              
              <div className="mt-8">
                <h3 className="font-heading italic text-3xl md:text-4xl tracking-[-1px] leading-none text-white mb-4">
                  {card.title}
                </h3>
                <p className="text-sm text-white/90 font-body font-light leading-snug max-w-[32ch]">
                  {card.body}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
