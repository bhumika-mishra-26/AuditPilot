import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Plus } from 'lucide-react';
import { cn } from '../../lib/utils';
import { LaserFlow } from './LaserFlow';
import masterSvg from '../../assets/master_orchestrator_v2_full.svg';

interface FAQProps {
  title?: string;
  subtitle?: string;
  categories: Record<string, string>;
  faqData: Record<string, { question: string; answer: string }[]>;
  className?: string;
}

export const FAQTabs = ({ 
  title = "FAQs",
  subtitle = "Frequently Asked Questions",
  categories,
  faqData,
  className,
  ...props 
}: FAQProps) => {
  const categoryKeys = Object.keys(categories);
  const [selectedCategory, setSelectedCategory] = useState(categoryKeys[0]);

  return (
    <section 
      id="faq"
      className={cn(
        "relative py-28 px-6 md:px-12",
        className
      )}
      {...props}
    >
      <div className="relative mx-auto max-w-20xl mt-20">
        {/* External Laser Flow (Falling on edge) */}
        {/* Origin with verticalBeamOffset -0.45 is 15px from bottom of 300px container.
            Setting bottom-full puts container exactly atop the box.
            TranslateY(15px) perfectly aligns origin with the border. */}
        <div 
          className="absolute bottom-full left-1/2 w-[100vw] h-[300px] z-[15] pointer-events-none opacity-90 mix-blend-screen"
          style={{ transform: 'translateX(-50%) translateY(15px)' }}
        >
          <LaserFlow
            horizontalBeamOffset={0.1}
            verticalBeamOffset={-0.45}
            color="#CF9EFF"
            wispDensity={1.2}
            fogIntensity={0.8}
            verticalSizing={4.0}
            horizontalSizing={0.3}
            flowSpeed={0.5}
          />
        </div>

        <div 
          className="relative w-full overflow-hidden rounded-[40px] border-2 border-[#FF79C6]/20 bg-[#060010] shadow-[0_10px_50px_rgba(255,121,198,0.05)] transition-all duration-500 hover:border-[#FF79C6]/40"
        >
        {/* Subtle Cyber Grid Background */}
        <div 
          className="absolute inset-0 z-0 opacity-[0.07]" 
          style={{
            backgroundImage: `
              radial-gradient(circle at 1px 1px, #CF9EFF 1px, transparent 0),
              linear-gradient(to right, #CF9EFF10 1px, transparent 1px),
              linear-gradient(to bottom, #CF9EFF10 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px, 40px 40px, 40px 40px',
          }}
        />

        <div className="relative z-20 py-20 px-6">
          <FAQHeader title={title} subtitle={subtitle} />
          <FAQTabsNav 
            categories={categories}
            selected={selectedCategory} 
            setSelected={setSelectedCategory} 
          />
          <FAQList 
            faqData={faqData}
            selected={selectedCategory} 
          />
        </div>
      </div>
    </div>
  </section>
);
};

const FAQHeader = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div className="relative z-10 flex flex-col items-center justify-center mb-12">
    <span className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider">
      {subtitle}
    </span>
    <h2 className="text-4xl md:text-5xl font-bold font-heading text-white">{title}</h2>
  </div>
);

const FAQTabsNav = ({ categories, selected, setSelected }: { categories: Record<string, string>, selected: string, setSelected: (v: string) => void }) => (
  <div className="relative z-10 flex flex-wrap items-center justify-center gap-3 px-6">
    {Object.entries(categories).map(([key, label]) => (
      <button
        key={key}
        onClick={() => setSelected(key)}
        className={cn(
          "relative overflow-hidden whitespace-nowrap rounded-xl border px-5 py-2.5 text-sm font-bold transition-all duration-300 shadow-sm",
          selected === key
            ? "border-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)]"
            : "border-white/10 bg-black/40 text-gray-400 hover:text-white hover:bg-white/5"
        )}
      >
        <span className="relative z-10">{label}</span>
        <AnimatePresence>
          {selected === key && (
            <motion.span
              initial={{ y: "100%" }}
              animate={{ y: "0%" }}
              exit={{ y: "100%" }}
              transition={{ duration: 0.5, ease: "backIn" }}
              className="absolute inset-0 z-0 bg-indigo-600"
            />
          )}
        </AnimatePresence>
      </button>
    ))}
  </div>
);

const FAQList = ({ faqData, selected }: { faqData: Record<string, {question: string, answer: string}[]>, selected: string }) => (
  <div className="mx-auto mt-12 max-w-3xl px-6 relative z-10">
    <AnimatePresence mode="wait">
      {Object.entries(faqData).map(([category, questions]) => {
        if (selected === category) {
          return (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="space-y-4"
            >
              {questions.map((faq, index) => (
                <FAQItem key={index} {...faq} />
              ))}
            </motion.div>
          );
        }
        return null;
      })}
    </AnimatePresence>
  </div>
);

const FAQItem = ({ question, answer }: { question: string, answer: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      animate={isOpen ? "open" : "closed"}
      className={cn(
        "rounded-2xl border transition-colors backdrop-blur-md overflow-hidden",
        isOpen ? "bg-indigo-500/10 border-indigo-500/30" : "bg-black/40 border-white/10 hover:bg-white/5"
      )}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between gap-4 p-6 text-left focus:outline-none"
      >
        <span
          className={cn(
            "text-lg font-bold transition-colors",
            isOpen ? "text-indigo-300" : "text-white"
          )}
        >
          {question}
        </span>
        <motion.span
          variants={{
            open: { rotate: "45deg" },
            closed: { rotate: "0deg" },
          }}
          transition={{ duration: 0.2 }}
          className="shrink-0 w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10"
        >
          <Plus
            className={cn(
              "h-4 w-4 transition-colors",
              isOpen ? "text-indigo-400" : "text-gray-400"
            )}
          />
        </motion.span>
      </button>
      <motion.div
        initial={false}
        animate={{ 
          height: isOpen ? "auto" : "0px", 
          opacity: isOpen ? 1 : 0
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="px-6"
      >
        <p className="text-gray-400 leading-relaxed pb-6 text-sm">{answer}</p>
      </motion.div>
    </motion.div>
  );
};
