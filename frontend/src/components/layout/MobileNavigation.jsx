import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, Database, Brain, Settings } from 'lucide-react';

export default function MobileNavigation() {
  const navItems = [
    { to: '/', label: 'Chat', icon: MessageSquare },
    { to: '/knowledge', label: 'Knowledge', icon: Database },
    { to: '/memory', label: 'Memory', icon: Brain },
    { to: '/settings', label: 'Status', icon: Settings },
  ];

  return (
    <div className="md:hidden fixed bottom-0 inset-x-0 bg-amethyst-dark border-t border-borderCol flex justify-around py-2 z-30">
      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center py-1 px-3 text-[11px] font-medium transition-colors ${
                isActive ? 'text-electric' : 'text-secondaryText hover:text-primaryText'
              }`
            }
          >
            <Icon className="w-5 h-5 mb-0.5" />
            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </div>
  );
}
