import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Database, Brain, Settings, GraduationCap } from 'lucide-react';

export default function Header() {
  const navItems = [
    { to: '/', label: 'Chat', icon: MessageSquare },
    { to: '/knowledge', label: 'Knowledge Base', icon: Database },
    { to: '/memory', label: 'Memory', icon: Brain },
    { to: '/settings', label: 'System Status', icon: Settings },
  ];

  return (
    <header className="h-16 border-b border-borderCol bg-amethyst-dark/95 backdrop-blur px-4 lg:px-6 flex items-center justify-between z-20">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-electric/20 border border-electric/40 flex items-center justify-center text-electric">
          <GraduationCap className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold text-primaryText tracking-tight">KBN University Assistant</h1>
            <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded-full bg-electric/15 text-lavender-soft border border-electric/30">
              Hybrid AI
            </span>
          </div>
          <p className="text-xs text-secondaryText hidden sm:block">
            Official knowledge assistant grounded in verified university portals
          </p>
        </div>
      </div>

      <nav className="hidden md:flex items-center space-x-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-electric text-white'
                    : 'text-secondaryText hover:text-primaryText hover:bg-amethyst-deep'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </header>
  );
}
