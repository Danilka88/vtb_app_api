
import React, { useState, useEffect, useRef } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { UserCircleIcon, SparklesIcon } from '../constants';
import { FinancialData } from '../types';
import { fetchFinancialData } from '../services/financialService';
import { GoogleGenAI } from '@google/genai';


interface Message {
  sender: 'user' | 'ai';
  text: string;
}

/**
 * Component: Assistant
 * 
 * Description:
 * Provides a chat interface powered by Google Gemini (gemini-2.5-flash).
 * Acts as a financial advisor by ingesting the user's aggregated financial data as context.
 * 
 * Logic:
 * 1. Fetches user's financial data (mocked via `fetchFinancialData`).
 * 2. Serializes `FinancialData` into JSON.
 * 3. Injects the JSON into the system prompt/content to ground the LLM's responses.
 * 4. Sends the prompt to the Gemini API via GoogleGenAI SDK.
 */
export const Assistant: React.FC = () => {
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchFinancialData();
      setFinancialData(data);
      setMessages([{
        sender: 'ai',
        text: "Здравствуйте! Я ваш финансовый ассистент. Чем могу помочь? \n\nСпросите меня, например: 'Проанализируй мои траты' или 'Как быстрее достичь цели?'"
      }]);
    };
    loadData();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !financialData) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });
      
      // System instruction defines the persona and formatting rules
      const systemInstruction = `You are a helpful and friendly financial assistant for a Russian user. Your name is Мультибанк Ассистент. Analyze the provided financial data and answer the user's questions in Russian. Provide concise, clear, and actionable financial advice. Use Markdown for formatting, especially bolding key terms with **term**. Do not use headers. Financial data will be provided in JSON format. All amounts are in RUB.`;

      // Context injection: The entire financial state is passed to the model
      const prompt = `Вот финансовые данные пользователя в формате JSON:
${JSON.stringify(financialData, null, 2)}

Вопрос пользователя: "${currentInput}"`;

      // Using gemini-2.5-flash for low latency response
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
        config: {
            systemInstruction: systemInstruction,
        }
      });
      
      const aiResponseText = response.text;
      
      const aiMessage: Message = { sender: 'ai', text: aiResponseText };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error fetching AI insights:", error);
      const errorMessage: Message = { sender: 'ai', text: "Извините, произошла ошибка. Пожалуйста, попробуйте позже." };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const parseText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => 
      part.startsWith('**') && part.endsWith('**')
        ? <strong key={i} className="font-bold text-white">{part.slice(2, -2)}</strong> 
        : part
    );
  }

  return (
    <div className="p-4 md:p-8 h-full flex flex-col">
      <h1 className="text-3xl font-bold text-white mb-6">Финансовый Ассистент</h1>
      <Card className="flex-1 flex flex-col max-h-[calc(100vh-200px)]">
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          {messages.map((msg, index) => (
            <div key={index} className={`flex items-start gap-4 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
              {msg.sender === 'ai' && (
                <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0">
                  <SparklesIcon className="w-6 h-6 text-white" />
                </div>
              )}
              <div className={`max-w-xl p-4 rounded-2xl ${msg.sender === 'ai' ? 'bg-slate-700 text-slate-200' : 'bg-blue-600 text-white'}`}>
                <p className="whitespace-pre-wrap">{parseText(msg.text)}</p>
              </div>
              {msg.sender === 'user' && (
                 <div className="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
                  <UserCircleIcon className="w-6 h-6 text-white" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
             <div className="flex items-start gap-4">
               <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0">
                  <SparklesIcon className="w-6 h-6 text-white" />
                </div>
                <div className="max-w-xl p-4 rounded-2xl bg-slate-700 text-slate-200">
                    <Spinner/>
                </div>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="p-4 border-t border-slate-700/50">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Спросите о ваших финансах..."
              className="w-full bg-slate-700 border border-slate-600 rounded-lg py-3 pl-4 pr-24 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-slate-500 disabled:cursor-not-allowed transition"
            >
              Отправить
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
