import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Account } from '../types';
import { ShoppingCartIcon, GasPumpIcon, PlaneIcon, RestaurantIcon } from '../constants';

const categoryIcons: { [key: string]: React.ReactNode } = {
    'Супермаркеты': <ShoppingCartIcon className="w-5 h-5" />,
    'АЗС': <GasPumpIcon className="w-5 h-5" />,
    'Путешествия': <PlaneIcon className="w-5 h-5" />,
    'Рестораны': <RestaurantIcon className="w-5 h-5" />,
};

export const VBankPay: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [loading, setLoading] = useState(true);
    const [isEnabled, setIsEnabled] = useState(false);
    const [includedAccounts, setIncludedAccounts] = useState<Set<string>>(new Set());
    const [selectedCategory, setSelectedCategory] = useState('Супермаркеты');

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setIsEnabled(financialData.smartPay.enabled);
            setIncludedAccounts(new Set(financialData.smartPay.includedAccountIds));
            setLoading(false);
        };
        loadData();
    }, []);
    
    const handleToggleAccount = (accountId: string) => {
        setIncludedAccounts(prev => {
            const newSet = new Set(prev);
            if (newSet.has(accountId)) {
                newSet.delete(accountId);
            } else {
                newSet.add(accountId);
            }
            return newSet;
        });
    };

    const bestCardForCategory = useMemo(() => {
        if (!data) return null;

        let bestCard: Account | null = null;
        let maxCashback = -1;

        const participatingAccounts = data.accounts.filter(acc => includedAccounts.has(acc.id));

        for (const account of participatingAccounts) {
            const bankCashback = data.cashbackCategories.find(c => c.bankName === account.bankName);
            if (bankCashback) {
                const cashbackRate = bankCashback.categories[selectedCategory] || 0;
                if (cashbackRate > maxCashback) {
                    maxCashback = cashbackRate;
                    bestCard = account;
                }
            }
        }
        
        return { card: bestCard, cashback: maxCashback };

    }, [data, selectedCategory, includedAccounts]);

    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Умная оплата</h1>
                        <p className="text-slate-400 mt-1">Автоматически выбираем лучшую карту для каждой покупки.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Максимум кэшбэка без усилий</h2>
                    <p className="text-slate-300">
                        Больше не нужно помнить условия по всем картам. Просто платите, а наш сервис сам выберет счет, с которого вы получите наибольший кэшбэк в конкретной категории трат.
                    </p>
                </Card>

                <Card className="p-6 mb-6">
                     <h3 className="text-lg font-semibold text-white mb-4">Симулятор выгоды</h3>
                     <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1">
                            <label htmlFor="category" className="block text-sm font-medium text-slate-400 mb-1">Категория покупки:</label>
                             <select id="category" value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition">
                                {Object.keys(categoryIcons).map(cat => <option key={cat} value={cat}>{cat}</option>)}
                             </select>
                        </div>
                        <div className="flex-1 p-4 rounded-lg bg-slate-900/50 text-center">
                            <p className="text-sm text-slate-400">Рекомендуемая карта для оплаты:</p>
                            {bestCardForCategory?.card ? (
                                <div className="flex items-center justify-center gap-2 mt-2">
                                     <span className="block w-1.5 h-6 rounded-full" style={{ backgroundColor: bestCardForCategory.card.brandColor }}></span>
                                     <p className="font-bold text-white text-lg">{bestCardForCategory.card.name}</p>
                                     <span className="text-green-400 font-semibold">({bestCardForCategory.cashback}% кэшбэк)</span>
                                </div>
                            ) : (
                                 <p className="font-bold text-white text-lg mt-2">Нет подходящей карты</p>
                            )}
                        </div>
                     </div>
                </Card>

                <Card className="p-6">
                    <div className="flex justify-between items-center pb-4 border-b border-slate-700/50">
                        <div>
                            <h3 className="text-lg font-semibold text-white">Статус сервиса</h3>
                            <p className="text-sm text-slate-400">Включите, чтобы покупки стали выгоднее.</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" checked={isEnabled} onChange={() => setIsEnabled(!isEnabled)} className="sr-only peer" />
                            <div className="w-14 h-8 bg-slate-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                    <div className={`mt-4 space-y-3 ${!isEnabled ? 'opacity-50 pointer-events-none' : ''}`}>
                         <h3 className="text-lg font-semibold text-white pt-2">Участвующие карты</h3>
                         {data.accounts.filter(acc => acc.type === 'debit' || acc.type === 'credit').map(account => (
                             <div key={account.id} className="flex justify-between items-center p-3 rounded-lg bg-slate-800 hover:bg-slate-700/50">
                                 <div className="flex items-center gap-3">
                                    <span className="block w-2 h-8 rounded-full" style={{ backgroundColor: account.brandColor }}></span>
                                    <div>
                                        <p className="font-medium text-white">{account.name}</p>
                                        <p className="text-sm text-slate-400">{account.bankName}</p>
                                    </div>
                                 </div>
                                 <label className="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" checked={includedAccounts.has(account.id)} onChange={() => handleToggleAccount(account.id)} className="sr-only peer" />
                                    <div className="w-11 h-6 bg-slate-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
                                </label>
                             </div>
                         ))}
                    </div>
                </Card>
            </div>
        </div>
    );
};