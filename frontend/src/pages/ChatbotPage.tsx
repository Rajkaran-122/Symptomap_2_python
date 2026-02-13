import { Chatbot } from '@/components/Chatbot';

const ChatbotPage = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-slate-50 flex flex-col items-center justify-center p-4 md:p-8">
            <div className="w-full max-w-5xl h-[85vh] bg-white rounded-[2.5rem] shadow-2xl shadow-indigo-100 overflow-hidden border border-white ring-1 ring-slate-900/5 flex flex-col md:flex-row">

                {/* Left Side: Brand & Context (Optional visual enhancement) */}
                <div className="hidden md:flex w-80 bg-slate-900 text-white p-8 flex-col justify-between relative overflow-hidden">
                    <div className="relative z-10">
                        <div className="w-12 h-12 bg-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/30">
                            <span className="text-2xl">🩺</span>
                        </div>
                        <h1 className="text-2xl font-bold mb-2">Dr. AI</h1>
                        <p className="text-slate-400 text-sm leading-relaxed">
                            Your personal AI health assistant. Analyze symptoms, check risks, and get instant medical guidance tailored to your region.
                        </p>
                    </div>

                    <div className="relative z-10 space-y-4">
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Capabilities</h3>
                            <ul className="text-sm text-slate-300 space-y-2">
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-emerald-400 rounded-full" /> Viral Detection</li>
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-blue-400 rounded-full" /> Symptom Analysis</li>
                                <li className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-indigo-400 rounded-full" /> Hospital Referral</li>
                            </ul>
                        </div>
                        <p className="text-[10px] text-slate-500">
                            Powered by SymptoMap Intelligence. Not a replacement for emergency care.
                        </p>
                    </div>

                    {/* Background noise/gradient */}
                    <div className="absolute top-0 left-0 w-full h-full opacity-10 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-repeat mix-blend-overlay"></div>
                    <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-indigo-600 rounded-full blur-3xl opacity-20"></div>
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 bg-white relative">
                    <Chatbot
                        variant="embedded"
                        isOpen={true}
                        initialLocation={{ city: 'Universal', country: 'India' }}
                    />
                </div>
            </div>
        </div>
    );
};

export default ChatbotPage;
