
import React, { useState, useEffect } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, FinancialHealth } from '../types';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { TrophyIcon, ChartBarSquareIcon, GiftIcon, ShieldCheckIcon, SparklesIcon } from '../constants';

export const FinancialHealthPage: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [healthData, setHealthData] = useState<FinancialHealth | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setHealthData(financialData.financialHealth);
            setLoading(false);
        };
        loadData();
    }, []);

    if (loading || !data || !healthData) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#22c55e'; // Green
        if (score >= 50) return '#eab308'; // Yellow
        return '#ef4444'; // Red
    };

    const scoreColor = getScoreColor(healthData.totalScore);
    
    const gaugeData = [
        { name: 'Score', value: healthData.totalScore, color: scoreColor },
        { name: 'Remaining', value: 100 - healthData.totalScore, color: '#334155' }
    ];

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-5xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Личное финансовое здоровье</h1>
                        <p className="text-slate-400 mt-1">Ваш рейтинг, достижения и награды за правильные финансовые привычки.</p>
                    </div>
                     <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Зарплатный сервис</div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Score Card */}
                    <Card className="p-6 flex flex-col items-center justify-center lg:col-span-1 bg-gradient-to-b from-slate-800 to-slate-900 border border-slate-700">
                        <h2 className="text-lg font-semibold text-slate-300 mb-4">Ваш рейтинг</h2>
                        <div className="relative w-48 h-48">
                             <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={gaugeData}
                                        cx="50%"
                                        cy="50%"
                                        startAngle={180}
                                        endAngle={0}
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {gaugeData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center mt-8">
                                <span className="text-5xl font-bold text-white">{healthData.totalScore}</span>
                                <span className="text-sm text-slate-400">из 100</span>
                            </div>
                        </div>
                        <p className="text-center text-slate-400 mt-2 text-sm">
                            Хороший результат! Вы входите в топ-15% зарплатных клиентов.
                        </p>
                    </Card>

                    {/* Components Breakdown */}
                    <Card className="p-6 lg:col-span-2">
                        <div className="flex items-center gap-2 mb-4">
                             <ChartBarSquareIcon className="w-6 h-6 text-blue-400" />
                             <h3 className="text-lg font-semibold text-white">Из чего складывается оценка?</h3>
                        </div>
                        
                        <div className="space-y-6">
                            {healthData.components.map(comp => {
                                const percent = (comp.score / comp.maxScore) * 100;
                                return (
                                    <div key={comp.id}>
                                        <div className="flex justify-between mb-1">
                                            <span className="text-white font-medium">{comp.label}</span>
                                            <span className={`text-sm font-bold ${comp.status === 'excellent' ? 'text-green-400' : comp.status === 'good' ? 'text-blue-400' : 'text-amber-400'}`}>
                                                {comp.score} / {comp.maxScore}
                                            </span>
                                        </div>
                                        <div className="w-full bg-slate-700 rounded-full h-2.5 mb-2">
                                            <div 
                                                className={`h-2.5 rounded-full transition-all duration-500 ${comp.status === 'excellent' ? 'bg-green-500' : comp.status === 'good' ? 'bg-blue-500' : 'bg-amber-500'}`} 
                                                style={{ width: `${percent}%` }}
                                            ></div>
                                        </div>
                                        <p className="text-xs text-slate-400 flex items-start gap-1">
                                            <SparklesIcon className="w-3 h-3 mt-0.5 flex-shrink-0" /> {comp.advice}
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    
                    {/* Badges / Achievements */}
                    <Card className="p-6">
                        <div className="flex items-center gap-2 mb-6">
                            <TrophyIcon className="w-6 h-6 text-yellow-400" />
                            <h3 className="text-lg font-semibold text-white">Ваши достижения</h3>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                            {healthData.badges.map(badge => (
                                <div key={badge.id} className={`flex flex-col items-center text-center p-3 rounded-lg border ${badge.unlocked ? 'bg-slate-800 border-yellow-500/30' : 'bg-slate-800/50 border-slate-700 opacity-50 grayscale'}`}>
                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 ${badge.unlocked ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-slate-700'}`}>
                                        {badge.unlocked ? <TrophyIcon className="w-6 h-6 text-white" /> : <ShieldCheckIcon className="w-6 h-6 text-slate-500" />}
                                    </div>
                                    <p className="text-sm font-bold text-white leading-tight">{badge.name}</p>
                                    <p className="text-[10px] text-slate-400 mt-1">{badge.description}</p>
                                </div>
                            ))}
                        </div>
                    </Card>

                    {/* Rewards Shop */}
                    <Card className="p-6">
                        <div className="flex items-center gap-2 mb-6">
                            <GiftIcon className="w-6 h-6 text-purple-400" />
                            <h3 className="text-lg font-semibold text-white">Награды за уровень</h3>
                        </div>
                        <div className="space-y-4">
                            {healthData.rewards.map(reward => (
                                <div key={reward.id} className={`relative p-4 rounded-lg border flex items-center gap-4 ${reward.isLocked ? 'border-slate-700 bg-slate-800/50' : 'border-purple-500/50 bg-slate-800'}`}>
                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${reward.isLocked ? 'bg-slate-700' : 'bg-purple-600'}`}>
                                        <GiftIcon className={`w-6 h-6 ${reward.isLocked ? 'text-slate-500' : 'text-white'}`} />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className={`font-bold ${reward.isLocked ? 'text-slate-400' : 'text-white'}`}>{reward.title}</h4>
                                        <p className="text-xs text-slate-500">{reward.description}</p>
                                    </div>
                                    
                                    {reward.isLocked ? (
                                         <div className="text-right">
                                            <p className="text-xs text-slate-500">Нужен рейтинг</p>
                                            <p className="font-bold text-slate-400">{reward.requiredScore}</p>
                                         </div>
                                    ) : (
                                        <button className="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-3 py-2 rounded transition">
                                            Активировать
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </Card>

                </div>
            </div>
        </div>
    );
};
