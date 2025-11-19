
import React, { useState, useEffect } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, BudgetPlan } from '../types';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { CalculatorIcon, SparklesIcon } from '../constants';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
});

export const SmartBudgeting: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [budget, setBudget] = useState<BudgetPlan | null>(null);
    const [loading, setLoading] = useState(true);
    
    // Local state to simulate interactivity with the "AI"
    const [simulatedIncome, setSimulatedIncome] = useState(0);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setBudget(financialData.budgetPlan);
            setSimulatedIncome(financialData.budgetPlan.totalMonthlyIncome);
            setLoading(false);
        };
        loadData();
    }, []);

    const handleRecalculate = () => {
        if (!budget) return;
        // Simulate simplistic re-calculation based on 50/30/20 rule
        const newBudget = { ...budget };
        newBudget.totalMonthlyIncome = simulatedIncome;
        newBudget.envelopes = [
            { ...budget.envelopes[0], allocatedAmount: simulatedIncome * 0.5 },
            { ...budget.envelopes[1], allocatedAmount: simulatedIncome * 0.3 },
            { ...budget.envelopes[2], allocatedAmount: simulatedIncome * 0.2 },
        ];
        // Update safe spend roughly
        const discretionary = newBudget.envelopes[1].allocatedAmount;
        const spentWants = budget.envelopes[1].spentAmount; // Assume spent stays same for demo
        newBudget.safeDailySpend = Math.max(0, (discretionary - spentWants) / budget.daysRemainingInMonth);
        
        setBudget(newBudget);
    };

    if (loading || !data || !budget) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    // Chart Data
    const chartData = budget.envelopes.map(env => ({
        name: env.name,
        value: env.allocatedAmount,
        color: env.color
    }));

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-5xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">AI Бюджетирование</h1>
                        <p className="text-slate-400 mt-1">Автопилот для вашего кошелька: распределяет, считает, советует.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Beta</div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Controls & Overview */}
                    <div className="lg:col-span-2 space-y-6">
                        
                        {/* Safe to Spend Card */}
                        <Card className="p-6 bg-gradient-to-r from-slate-800 to-slate-900 border-l-4 border-green-500">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-slate-400 font-medium mb-1">Безопасный расход на сегодня</p>
                                    <h2 className="text-5xl font-bold text-white tracking-tight">{currencyFormatter.format(budget.safeDailySpend)}</h2>
                                    <p className="text-sm text-slate-500 mt-2">Если вы потратите меньше, остаток перенесется на завтра.</p>
                                </div>
                                <div className="bg-slate-800 p-3 rounded-full">
                                    <CalculatorIcon className="w-8 h-8 text-green-400" />
                                </div>
                            </div>
                        </Card>

                        {/* Envelopes */}
                        <Card className="p-6">
                            <h3 className="text-xl font-semibold text-white mb-4">Мои конверты</h3>
                            <div className="space-y-6">
                                {budget.envelopes.map(env => {
                                    const percentUsed = Math.min(100, (env.spentAmount / env.allocatedAmount) * 100);
                                    const isOverBudget = env.spentAmount > env.allocatedAmount;
                                    
                                    return (
                                        <div key={env.id}>
                                            <div className="flex justify-between items-end mb-1">
                                                <div>
                                                    <span className="text-white font-medium text-lg">{env.name}</span>
                                                    <span className={`text-xs ml-2 px-2 py-0.5 rounded ${env.type === 'savings' ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'}`}>
                                                        {env.type === 'essentials' ? 'Обязательно' : env.type === 'savings' ? 'Цель' : 'Гибко'}
                                                    </span>
                                                </div>
                                                <div className="text-right">
                                                    <span className={`font-bold ${isOverBudget ? 'text-red-400' : 'text-white'}`}>
                                                        {currencyFormatter.format(env.spentAmount)}
                                                    </span>
                                                    <span className="text-slate-500 text-sm"> / {currencyFormatter.format(env.allocatedAmount)}</span>
                                                </div>
                                            </div>
                                            
                                            {/* Progress Bar */}
                                            <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden relative">
                                                <div 
                                                    className="h-full transition-all duration-500 rounded-full" 
                                                    style={{ width: `${percentUsed}%`, backgroundColor: env.color }}
                                                ></div>
                                                {/* Forecast marker (simplified for demo) */}
                                                {env.forecastedAmount > env.allocatedAmount && (
                                                     <div 
                                                        className="absolute top-0 bottom-0 w-1 bg-red-500/80 z-10 animate-pulse"
                                                        style={{ left: `${(env.allocatedAmount / env.forecastedAmount) * 100}%` }}
                                                        title="Прогноз превышения"
                                                     ></div>
                                                )}
                                            </div>
                                            
                                            {env.forecastedAmount > env.allocatedAmount && (
                                                <p className="text-xs text-red-400 mt-1">
                                                    ⚠️ Прогноз: перерасход на {currencyFormatter.format(env.forecastedAmount - env.allocatedAmount)} к концу месяца
                                                </p>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </Card>
                    </div>

                    {/* Right Column: AI Config & Insights */}
                    <div className="space-y-6">
                        
                        {/* Income Config */}
                         <Card className="p-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Настройки бюджета</h3>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Ежемесячный доход</label>
                                <div className="flex gap-2">
                                    <input 
                                        type="number" 
                                        value={simulatedIncome} 
                                        onChange={(e) => setSimulatedIncome(parseInt(e.target.value) || 0)}
                                        className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2 text-white"
                                    />
                                    <button 
                                        onClick={handleRecalculate}
                                        className="bg-blue-600 px-4 rounded-lg hover:bg-blue-700 text-white"
                                    >
                                        OK
                                    </button>
                                </div>
                                <p className="text-xs text-slate-500 mt-2">
                                    Агент использует правило 50/30/20 для автоматического распределения.
                                </p>
                            </div>
                            
                            <div className="h-48 w-full mt-6">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie 
                                            data={chartData} 
                                            innerRadius={40} 
                                            outerRadius={70} 
                                            paddingAngle={5} 
                                            dataKey="value"
                                            stroke="none"
                                        >
                                            {chartData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Pie>
                                        <Tooltip formatter={(val: number) => currencyFormatter.format(val)} contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff'}} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>

                        {/* AI Insights */}
                        <Card className="p-6 bg-slate-800/50 border border-purple-500/30 relative overflow-hidden">
                            <div className="absolute -right-4 -top-4 bg-purple-500/20 w-24 h-24 rounded-full blur-2xl"></div>
                            
                            <div className="flex items-center gap-2 mb-4">
                                <SparklesIcon className="w-5 h-5 text-purple-400" />
                                <h3 className="font-semibold text-white">AI Советы</h3>
                            </div>

                            <div className="space-y-4">
                                {budget.insights.map((insight, idx) => (
                                    <div key={idx} className="text-sm text-slate-300 p-3 bg-slate-900/50 rounded-lg border-l-2 border-purple-500">
                                        {insight}
                                    </div>
                                ))}
                            </div>
                        </Card>

                    </div>
                </div>
            </div>
        </div>
    );
};
