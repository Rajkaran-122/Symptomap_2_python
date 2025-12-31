
import React from 'react';
import { Bell, Search, Menu, User } from 'lucide-react';

const Header = () => {
    return (
        <header className="fixed top-0 left-0 right-0 h-16 bg-gradient-to-r from-primary-900 to-primary-800 text-white z-40 shadow-md flex items-center justify-between px-6">
            {/* Left: Branding */}
            <div className="flex items-center w-[240px]">
                <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3 shadow-lg ring-2 ring-blue-400/30">
                    <span className="font-bold text-white">SM</span>
                </div>
                <div>
                    <h1 className="text-xl font-bold tracking-tight">SymptoMap</h1>
                    <p className="text-[10px] text-blue-200 uppercase tracking-widest font-semibold">Intelligence</p>
                </div>
            </div>

            {/* Center: Search (Optional) */}
            <div className="hidden md:flex items-center flex-1 max-w-xl mx-8">
                <div className="relative w-full">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-primary-300" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search hospitals, diseases, or zones..."
                        className="block w-full pl-10 pr-3 py-2 border border-transparent rounded-lg leading-5 bg-primary-800/50 text-white placeholder-primary-300 focus:outline-none focus:bg-primary-800 focus:ring-1 focus:ring-primary-400 sm:text-sm transition-all"
                    />
                </div>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center space-x-4">
                <button className="p-2 rounded-full hover:bg-white/10 transition-colors relative">
                    <Bell className="w-5 h-5 text-primary-100" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-critical rounded-full border border-primary-900"></span>
                </button>

                <div className="h-8 w-px bg-primary-700 mx-2"></div>

                <button className="flex items-center space-x-3 hover:bg-white/10 p-2 rounded-lg transition-colors">
                    <div className="text-right hidden md:block">
                        <p className="text-sm font-medium text-white">Dr. User</p>
                        <p className="text-xs text-primary-300">Admin</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-primary-200 flex items-center justify-center text-primary-900 ring-2 ring-white/20">
                        <User className="w-5 h-5" />
                    </div>
                </button>
            </div>
        </header>
    );
};

export default Header;
