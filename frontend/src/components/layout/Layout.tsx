
import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
            {/* Fixed Header */}
            <Header />

            <div className="flex flex-1 pt-16">
                {/* Fixed Sidebar */}
                <Sidebar />

                {/* Main Content Area */}
                <main className="flex-1 ml-[240px] p-6 lg:p-8 overflow-y-auto min-h-[calc(100vh-64px)]">
                    <div className="max-w-[1920px] mx-auto animate-fade-in">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;
