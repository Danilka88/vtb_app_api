
import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, MarketplaceSubscription, Account } from '../types';
import { SparklesIcon } from '../constants';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 1, // Allow 1 decimal for small amounts
});

interface Recommendation extends MarketplaceSubscription {
    totalSpent: number;
    potentialSaving: number;
}

const SubscriptionCard: React.FC<{ sub: Recommendation; accounts: Account[]; cashbackData: FinancialData['cashbackCategories'] }> = ({ sub, accounts, cashbackData }) => {
    const [showPayment, setShowPayment] = useState(false);
    const [isSubscribed, setIsSubscribed] = useState(false);

    const bestCardForSubscription = useMemo(() => {
        let bestCard: Account | null = null;
        let maxCashback = -1;

        const debitCards = accounts.filter(acc => acc.type === 'debit');

        for (const account of debitCards) {
            const bankCashback = cashbackData.find(c => c.bankName === account.bankName);
            if (bankCashback) {
                const cashbackRate = bankCashback.categories[sub.cashbackCategory] || 0;
                if (cashbackRate > maxCashback) {
                    maxCashback = cashbackRate;
                    bestCard = account;
                }
            }
        }
        return { card: bestCard, cashback: maxCashback > 0 ? maxCashback : null };
    }, [accounts, cashbackData, sub.cashbackCategory]);
    
    // Calculate percentage saving
    const savingPercent = sub.totalSpent > 0 
        ? Math.round((sub.potentialSaving / sub.totalSpent) * 100) 
        : 0;

    if (isSubscribed) {
        return (
             <Card className="p-5 flex flex-col justify-between border-green-500/50">
                 <div className="text-center py-10">
                    <div className="w-16 h-16 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                    </div>
                    <h3 className="text-xl font-bold text-green-400">Вы успешно подписались!</h3>
                    <p className="text-slate-300 mt-2">Подписка "{sub.name}" теперь активна.</p>
                 </div>
            </Card>
        );
    }

    return (
        <Card className="p-5 flex flex-col justify-between hover:shadow-purple-500/20 hover:border-purple-500/50 transition-all duration-300">
            <div>
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-14 h-14 bg-slate-700 rounded-xl flex items-center justify-center shadow-inner">
                        <span className="text-2xl font-bold text-white">{sub.name.charAt(0)}</span>
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">{sub.name}</h3>
                        <p className="text-lg font-semibold text-purple-400">{currencyFormatter.format(sub.cost)}<span className="text-sm text-slate-400 font-normal">/мес</span></p>
                    </div>
                </div>
                
                {/* Redesigned Benefit Block */}
                <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-green-500/30 rounded-xl p-4 mb-6 relative overflow-hidden group">
                     <div className="absolute top-0 right-0 w-20 h-20 bg-green-500/10 rounded-full -mr-10 -mt-10 blur-2xl"></div>
                     
                     <div className="flex items-center gap-2 mb-3">
                        <SparklesIcon className="w-4 h-4 text-green-400" />
                        <h4 className="font-bold text-green-400 text-xs uppercase tracking-wider">Прогноз выгоды</h4>
                     </div>

                     <div className="flex items-end justify-between gap-2">
                        <div>
                             <p className="text-[10px] text-slate-400 uppercase font-semibold tracking-wide mb-1">Ваши траты</p>
                             <p className="text-slate-300 font-medium text-sm">{currencyFormatter.format(sub.totalSpent)}</p>
                        </div>
                        
                        <div className="h-8 w-px bg-slate-700/50 mx-2"></div>

                        <div className="text-right">
                             <div className="flex items-center justify-end gap-1.5 mb-0.5">
                                <span className="bg-green-500 text-slate-900 text-[10px] font-bold px-1.5 py-0.5 rounded leading-none">
                                   -{savingPercent}%
                                </span>
                                <p className="text-[10px] text-green-400/80 uppercase font-semibold tracking-wide">Экономия</p>
                             </div>
                             <p className="text-2xl font-bold text-green-400 leading-none tracking-tight">
                                {currencyFormatter.format(sub.potentialSaving)}
                             </p>
                        </div>
                     </div>
                </div>
                
                <h4 className="font-semibold text-white text-sm mb-3">Преимущества подписки:</h4>
                <ul className="space-y-2">
                    {sub.benefits.map(benefit => (
                        <li key={benefit} className="flex items-start gap-2 text-sm text-slate-300">
                             <svg className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            <span>{benefit}</span>
                        </li>
                    ))}
                </ul>
            </div>
            
            <div className="mt-6 pt-4 border-t border-slate-700/50">
                 {showPayment && bestCardForSubscription.card && (
                    <div className="mb-4 p-3 bg-slate-900 rounded-lg border border-slate-700">
                        <p className="text-xs text-slate-400 mb-2">Рекомендуемая карта для оплаты:</p>
                        <div className="flex items-center gap-3">
                             <span className="block w-1.5 h-8 rounded-full" style={{ backgroundColor: bestCardForSubscription.card.brandColor }}></span>
                             <div>
                                 <p className="font-bold text-white text-sm">{bestCardForSubscription.card.name}</p>
                                 <p className="text-xs text-slate-400">{bestCardForSubscription.card.bankName} •••• {bestCardForSubscription.card.last4}</p>
                             </div>
                             {bestCardForSubscription.cashback && (
                                 <span className="ml-auto text-xs font-bold text-green-400 bg-green-400/10 px-2 py-1 rounded">
                                     +{bestCardForSubscription.cashback}% кэшбэк
                                 </span>
                             )}
                        </div>
                    </div>
                )}
                <button
                    onClick={() => {
                        if (showPayment) {
                            setIsSubscribed(true);
                        } else {
                            setShowPayment(true);
                        }
                    }}
                    className="w-full bg-purple-600 text-white font-semibold py-3 rounded-lg hover:bg-purple-700 transition shadow-lg shadow-purple-900/20"
                >
                    {showPayment ? `Оплатить ${currencyFormatter.format(sub.cost)}` : 'Оформить подписку'}
                </button>
            </div>
        </Card>
    );
};

export const SubscriptionMarketplace: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setLoading(false);
        };
        loadData();
    }, []);

    const recommendations = useMemo((): Recommendation[] => {
        if (!data) return [];
        const recommendedSubs: Recommendation[] = [];
        const oneMonthAgo = new Date();
        oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);

        const recentTransactions = data.transactions.filter(t => new Date(t.date) > oneMonthAgo && t.type === 'expense');

        for (const sub of data.marketplaceSubscriptions) {
            const relatedTransactions = recentTransactions.filter(t => sub.relatedMerchants.includes(t.description));
            const totalSpent = relatedTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
            
            // Recommend if spent more than the subscription cost
            if (totalSpent > sub.cost) {
                // Assuming a 10% average saving for demonstration
                const potentialSaving = totalSpent * 0.10;
                recommendedSubs.push({ ...sub, totalSpent, potentialSaving });
            }
        }
        return recommendedSubs;
    }, [data]);
    
    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Маркетплейс подписок</h1>
                        <p className="text-slate-400 mt-1">Подписки, которые действительно вам нужны.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase shadow-lg shadow-yellow-900/20">Premium</div>
                </div>

                <Card className="p-6 mb-8 bg-gradient-to-r from-slate-800 to-slate-900 border-slate-700">
                    <h2 className="text-xl font-semibold text-white mb-2">Экономьте на привычных тратах</h2>
                    <p className="text-slate-300 leading-relaxed">
                        Мы проанализировали ваши расходы и подобрали подписки, которые помогут вам получать больше выгоды от любимых сервисов. Каждая рекомендация основана на ваших реальных транзакциях.
                    </p>
                </Card>

                {recommendations.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {recommendations.map(sub => (
                           <SubscriptionCard 
                                key={sub.id} 
                                sub={sub} 
                                accounts={data.accounts}
                                cashbackData={data.cashbackCategories}
                           />
                        ))}
                    </div>
                ) : (
                     <Card className="p-10 text-center">
                        <h3 className="text-xl font-semibold text-white">Для вас пока нет рекомендаций</h3>
                        <p className="text-slate-400 mt-2">Продолжайте пользоваться картами, и мы подберем для вас выгодные предложения, как только они появятся.</p>
                     </Card>
                )}
            </div>
        </div>
    );
};
