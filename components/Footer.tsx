import React from 'react';
import { Terminal, Github, Twitter, Linkedin } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-black border-t border-zinc-900 py-12 text-sm">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
        
        <div className="flex items-center gap-2">
          <Terminal className="text-brand-600 w-5 h-5" />
          <span className="font-mono font-bold text-zinc-200">
            GÔNDOLA.AI <span className="text-zinc-600 ml-2">© 2024</span>
          </span>
        </div>

        <div className="flex items-center gap-6 text-zinc-500 font-mono">
          <a href="#" className="hover:text-brand-400 transition-colors">PRIVACIDADE</a>
          <a href="#" className="hover:text-brand-400 transition-colors">TERMOS</a>
          <a href="#" className="hover:text-brand-400 transition-colors">STATUS</a>
        </div>

        <div className="flex items-center gap-4">
          <a href="#" className="text-zinc-500 hover:text-white transition-colors"><Github size={20} /></a>
          <a href="#" className="text-zinc-500 hover:text-white transition-colors"><Twitter size={20} /></a>
          <a href="#" className="text-zinc-500 hover:text-white transition-colors"><Linkedin size={20} /></a>
        </div>

      </div>
    </footer>
  );
};

export default Footer;