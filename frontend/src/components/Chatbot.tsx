/*
 * React Chatbot Component for SymptoMap AI Doctor
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Message {
    role: 'user' | 'assistant' | 'system';
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
}

export const Chatbot: React.FC<ChatbotProps> = ({ onClose, initialLocation }) => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationState, setConversationState] = useState('');
    const [completion, setCompletion] = useState(0);
    const [healthAlert, setHealthAlert] = useState<string | null>(null);
    const [showDisclaimer, setShowDisclaimer] = useState(true);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Start conversation on mount
    useEffect(() => {
        startConversation();
    }, []);

    const startConversation = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/chatbot/start`, {
                user_info: null,
                location: initialLocation
            });

            setSessionId(response.data.session_id);
            setConversationState(response.data.conversation_state);

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
                message: input
            });

            const botMessages = response.data.bot_messages.map((msg: any) => ({
                role: 'assistant' as const,
                content: msg.content,
                timestamp: msg.timestamp || new Date().toISOString(),
                type: msg.type
            }));

            setMessages(prev => [...prev, ...botMessages]);
            setConversationState(response.data.conversation_state);
            setCompletion(response.data.completion_percentage || 0);
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

    const endConversation = async () => {
        if (!sessionId) return;

        setIsLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/chatbot/end`, {
                session_id: sessionId
            });

            // Show assessment
            const assessment = response.data.assessment;
            const recommendations = response.data.recommendations;

            const summaryMessage: Message = {
                role: 'assistant',
                content: `
**Assessment Complete**

**Severity:** ${assessment.severity.toUpperCase()}

**Primary Diagnosis:** ${assessment.primary_diagnosis.condition} (${(assessment.primary_diagnosis.confidence * 100).toFixed(0)}% confidence)

**Recommendations:**
${recommendations.home_care ? '- ' + recommendations.home_care.join('\n- ') : ''}

**When to See a Doctor:**
${recommendations.when_to_see_doctor?.routine ? recommendations.when_to_see_doctor.routine.join('\n') : ''}

You can download your full SOAP note and recommendations report.
        `,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, summaryMessage]);
        } catch (error) {
            console.error('Failed to end conversation:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen max-h-[800px] bg-white rounded-lg shadow-2xl">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-4 rounded-t-lg">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold">AI Health Assistant</h2>
                        <p className="text-sm opacity-90">
                            {conversationState === 'greeting' && 'Welcome!'}
                            {conversationState === 'symptom_collection' && 'Collecting symptoms...'}
                            {conversationState === 'history_collection' && 'Medical history...'}
                            {conversationState === 'assessment' && 'Assessing...'}
                        </p>
                    </div>
                    {onClose && (
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2"
                        >
                            ✕
                        </button>
                    )}
                </div>

                {/* Progress bar */}
                <div className="mt-2 bg-white bg-opacity-30 rounded-full h-2">
                    <div
                        className="bg-white h-2 rounded-full transition-all duration-500"
                        style={{ width: `${completion}%` }}
                    />
                </div>
            </div>

            {/* Health Alert */}
            {healthAlert && (
                <div className="bg-amber-100 border-l-4 border-amber-500 p-3 m-3 rounded">
                    <p className="text-sm text-amber-800">⚠️ {healthAlert}</p>
                </div>
            )}

            {/* Medical Disclaimer */}
            {showDisclaimer && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-3 m-3 rounded">
                    <div className="flex justify-between items-start">
                        <p className="text-xs text-blue-800">
                            ⚕️ <strong>Medical Disclaimer:</strong> This AI provides general health information only
                            and is not a substitute for professional medical advice. For emergencies, call 911.
                        </p>
                        <button
                            onClick={() => setShowDisclaimer(false)}
                            className="text-blue-600 hover:text-blue-800 ml-2"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                ? 'bg-emerald-600 text-white'
                                : msg.type === 'emergency'
                                    ? 'bg-red-100 border-2 border-red-500 text-red-900'
                                    : msg.role === 'system'
                                        ? 'bg-gray-200 text-gray-800'
                                        : 'bg-gray-100 text-gray-900'
                                }`}
                        >
                            <p className="text-sm whitespace-pre-line">{msg.content}</p>
                            <p className="text-xs opacity-70 mt-1">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg p-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4 bg-gray-50">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Type your message..."
                        className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        disabled={isLoading || conversationState === 'completed'}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="bg-emerald-600 text-white px-6 py-2 rounded-lg hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                        Send
                    </button>
                </div>

                {conversationState === 'assessment' && (
                    <button
                        onClick={endConversation}
                        className="mt-2 w-full bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
                    >
                        Get Final Assessment
                    </button>
                )}
            </div>
        </div>
    );
};

export default Chatbot;
