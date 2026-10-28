import React from 'react';
import { GraduationCap, Sparkles, Compass, HelpCircle, ShieldCheck } from 'lucide-react';

export default function WelcomeScreen({ onSelectStarter }) {
  const starters = [
    { text: 'Tell me about KBN University.', icon: Compass },
    { text: 'Where can I find information about academic programmes?', icon: GraduationCap },
    { text: 'How can I check admission eligibility?', icon: HelpCircle },
    { text: 'Where can I find official university notices?', icon: Sparkles },
    { text: 'How can I contact the university?', icon: ShieldCheck },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto animate-fadeIn">
      <div className="w-16 h-16 rounded-2xl bg-electric/20 border border-electric/40 flex items-center justify-center text-electric mb-5 shadow-xl">
        <GraduationCap className="w-10 h-10" />
      </div>

      <h2 className="text-2xl font-bold text-primaryText tracking-tight mb-2">
        KBN University Assistant
      </h2>
      <p className="text-sm text-secondaryText leading-relaxed mb-8 max-w-lg">
        Ask questions regarding academic programs, faculties, admission guidelines,
        campus location, and administrative contact channels. All institutional answers are grounded
        directly in verified pages from <span className="text-lavender-soft font-medium">kbn.university</span>.
      </p>

      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
        {starters.map((starter, idx) => {
          const Icon = starter.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectStarter(starter.text)}
              className="p-3.5 rounded-xl bg-surface hover:bg-amethyst-deep border border-borderCol hover:border-electric/50 text-secondaryText hover:text-primaryText transition-all flex items-start space-x-3 group text-sm shadow-sm"
            >
              <Icon className="w-5 h-5 text-electric mt-0.5 group-hover:scale-110 transition-transform flex-shrink-0" />
              <span className="font-medium leading-snug">{starter.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
