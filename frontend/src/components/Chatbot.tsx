/*
 * React Chatbot Component for SymptoMap AI Doctor
 * Premium UI with Markdown Support and Voice Integration
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
    Send, Mic,
    Bot, User as UserIcon,
    AlertTriangle, ChevronDown
} from 'lucide-react';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Message {
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
    timestamp: string;
    type?: 'text' | 'emergency';
}

interface ChatbotProps {
    onClose?: () => void;
    initialLocation?: {
        city: string;
        country: string;
    };
    userName?: string;
    isOpen?: boolean;
    variant?: 'popup' | 'embedded';
}

export const Chatbot: React.FC<ChatbotProps> = ({ onClose, initialLocation, userName, isOpen = false, variant = 'popup' }) => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [healthAlert, setHealthAlert] = useState<string | null>(null);

    // Voice Mode State (Placeholder for now)
    const [isListening, setIsListening] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    // Focus input when opened
    useEffect(() => {
        if ((isOpen || variant === 'embedded') && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen, variant]);

    // Start conversation on first open if no session
    useEffect(() => {
        if ((isOpen || variant === 'embedded') && !sessionId) {
            startConversation();
        }
    }, [isOpen, variant]);

    const startConversation = async () => {
        try {
            setIsLoading(true);
            // Construct user info context if available
            const userInfo = userName ? { name: userName } : null;

            const response = await axios.post(`${API_BASE_URL}/chatbot/start`, {
                user_info: userInfo,
                location: initialLocation
            });

            setSessionId(response.data.session_id);

            if (response.data.local_health_alert) {
                setHealthAlert(response.data.local_health_alert);
            }

            setMessages([{
                role: 'assistant',
                content: response.data.message,
                timestamp: new Date().toISOString()
            }]);
        } catch (error) {
            console.error('Failed to start conversation:', error);
            setMessages([{
                role: 'system',
                content: 'Failed to connect to AI assistant. Please try again later.',
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || !sessionId) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/chatbot/message`, {
                session_id: sessionId,
                message: userMessage.content
            });

            const botMessages = response.data.bot_messages.map((msg: any) => ({
                role: 'assistant' as const,
                content: msg.content,
                timestamp: msg.timestamp || new Date().toISOString(),
                type: msg.type
            }));

            setMessages(prev => [...prev, ...botMessages]);
        } catch (error) {
            console.error('Failed to send message:', error);
            setMessages(prev => [...prev, {
                role: 'system',
                content: 'Failed to get response. Please try again.',
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVoiceClick = () => {
        setIsListening(!isListening);
        // Placeholder interaction
        if (!isListening) {
            setTimeout(() => {
                setIsListening(false);
                alert("Voice mode is coming soon! For now, please type your message.");
            }, 1000);
        }
    };

    if (!isOpen && variant === 'popup') return null;

    const containerClasses = variant === 'embedded'
        ? 'w-full h-full flex flex-col bg-white'
        : 'fixed bottom-24 right-6 w-[400px] h-[600px] max-h-[80vh] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-slate-200 z-50 animate-in slide-in-from-bottom-10 fade-in duration-300';

    return (
        <div className={containerClasses}>
            {/* Header */}
            <div className="bg-indigo-600 p-4 flex items-center justify-between shadow-md z-10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center border-2 border-indigo-400">
                        <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-white text-md leading-tight">AI Health Assistant</h3>
                        <p className="text-indigo-200 text-xs flex items-center gap-1">
                            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                            Online • {initialLocation?.city || 'Universal'}
                        </p>
                    </div>
                </div>
                {variant === 'popup' && (
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-indigo-500 rounded-full text-white transition-colors"
                    >
                        <ChevronDown className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Health Alert Banner */}
            {healthAlert && (
                <div className="bg-amber-50 border-b border-amber-100 px-4 py-2 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-amber-800 font-medium">{healthAlert}</p>
                </div>
            )}

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-5 bg-slate-50 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                {messages.map((msg, idx) => {
                    const isUser = msg.role === 'user';
                    const isSystem = msg.role === 'system';
                    const isEmergency = msg.type === 'emergency';

                    if (isSystem) {
                        return (
                            <div key={idx} className="flex justify-center">
                                <span className="bg-slate-200 text-slate-600 text-xs px-3 py-1 rounded-full">
                                    {msg.content}
                                </span>
                            </div>
                        );
                    }

                    return (
                        <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                            {!isUser && (
                                <div className="w-8 h-8 rounded-full bg-white border border-slate-100 flex items-center justify-center mr-2 shadow-sm flex-shrink-0">
                                    {isEmergency ? <AlertTriangle className="w-5 h-5 text-red-500" /> : <Bot className="w-5 h-5 text-indigo-600" />}
                                </div>
                            )}

                            <div className={`
                                max-w-[80%] rounded-2xl p-3.5 shadow-sm text-sm leading-relaxed
                                ${isUser
                                    ? 'bg-indigo-600 text-white rounded-br-none'
                                    : isEmergency
                                        ? 'bg-red-50 text-red-900 border border-red-100 rounded-bl-none'
                                        : 'bg-white text-slate-700 border border-slate-100 rounded-bl-none'
                                }
                            `}>
                                {isUser ? (
                                    <p>{msg.content}</p>
                                ) : (
                                    <div className="markdown-content space-y-2">
                                        <ReactMarkdown
                                            components={{
                                                strong: ({ node, ...props }) => <span className="font-bold text-indigo-900" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-1" {...props} />,
                                                ol: ({ node, ...props }) => <ol className="list-decimal pl-4 space-y-1" {...props} />,
                                                table: ({ node, ...props }) => <div className="overflow-x-auto my-2 rounded-lg border border-slate-200"><table className="min-w-full divide-y divide-slate-200" {...props} /></div>,
                                                th: ({ node, ...props }) => <th className="bg-slate-50 px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase tracking-wider" {...props} />,
                                                td: ({ node, ...props }) => <td className="px-3 py-2 whitespace-nowrap text-xs text-slate-600 border-t border-slate-100" {...props} />,
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                )}
                                <p className={`text-[10px] mt-1.5 ${isUser ? 'text-indigo-200' : 'text-slate-400'}`}>
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </p>
                            </div>

                            {isUser && (
                                <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center ml-2 flex-shrink-0">
                                    <UserIcon className="w-5 h-5 text-indigo-600" />
                                </div>
                            )}
                        </div>
                    );
                })}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="w-8 h-8 rounded-full bg-white border border-slate-100 flex items-center justify-center mr-2 shadow-sm">
                            <Bot className="w-5 h-5 text-indigo-600" />
                        </div>
                        <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-none p-4 shadow-sm flex items-center gap-1.5">
                            <span className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-slate-100">
                <div className="relative flex items-center gap-2">
                    <button
                        onClick={handleVoiceClick}
                        className={`p-3 rounded-xl transition-all ${isListening
                            ? 'bg-red-100 text-red-600 animate-pulse'
                            : 'bg-slate-100 text-slate-500 hover:bg-indigo-50 hover:text-indigo-600'
                            }`}
                        title="Voice Mode (Coming Soon)"
                    >
                        <Mic className="w-5 h-5" />
                    </button>

                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Type your symptoms..."
                        className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
                        disabled={isLoading}
                    />

                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="p-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-indigo-200 active:scale-95"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
                <div className="mt-2 text-center">
                    <p className="text-[10px] text-slate-400">
                        Response times may vary based on complex queries.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Chatbot;
