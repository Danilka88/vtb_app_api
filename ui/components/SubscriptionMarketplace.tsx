import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, MarketplaceSubscription, Account } from '../types';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
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
    
    if (isSubscribed) {
        return (
             <Card className="p-5 flex flex-col justify-between border-green-500/50">
                 <div className="text-center">
                    <h3 className="text-xl font-bold text-green-400">Вы успешно подписались!</h3>
                    <p className="text-slate-300 mt-2">Подписка "{sub.name}" теперь активна.</p>
                 </div>
            </Card>
        );
    }

    return (
        <Card className="p-5 flex flex-col justify-between hover:shadow-purple-500/20 hover:border-purple-500/50 transition-all duration-300">
            <div>
                <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 bg-slate-700 rounded-lg flex items-center justify-center">
                        <span className="text-2xl font-bold">{sub.name.charAt(0)}</span>
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">{sub.name}</h3>
                        <p className="text-lg font-semibold text-purple-400">{currencyFormatter.format(sub.cost)}<span className="text-sm text-slate-400">/мес</span></p>
                    </div>
                </div>
                
                <div className="p-3 rounded-lg bg-green-500/10 mb-4">
                    <h4 className="font-semibold text-green-300 text-sm">Почему это выгодно для вас?</h4>
                    <p className="text-slate-200 text-sm mt-1">
                        За последний месяц вы потратили <span className="font-bold">{currencyFormatter.format(sub.totalSpent)}</span> на связанные сервисы. С этой подпиской вы могли бы сэкономить около <span className="font-bold">{currencyFormatter.format(sub.potentialSaving)}</span>.
                    </p>
                </div>
                
                <h4 className="font-semibold text-white mb-2">Что вы получите:</h4>
                <ul className="list-disc list-inside text-slate-300 space-y-1 text-sm">
                    {sub.benefits.map(benefit => <li key={benefit}>{benefit}</li>)}
                </ul>
            </div>
            
            <div className="mt-5">
                 {showPayment && bestCardForSubscription.card && (
                    <div className="mb-4 p-3 bg-slate-900/50 rounded-lg">
                        <p className="text-sm text-slate-400">Рекомендуемая карта для оплаты:</p>
                        <div className="flex items-center gap-2 mt-1">
                             <span className="block w-1.5 h-6 rounded-full" style={{ backgroundColor: bestCardForSubscription.card.brandColor }}></span>
                             <p className="font-bold text-white">{bestCardForSubscription.card.name}</p>
                             {bestCardForSubscription.cashback && <span className="text-green-400 font-semibold">({bestCardForSubscription.cashback}% кэшбэк)</span>}
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
                    className="w-full bg-purple-600 text-white font-semibold py-2.5 rounded-lg hover:bg-purple-700 transition"
                >
                    {showPayment ? `Подтвердить и оплатить` : 'Оформить подписку'}
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
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Экономьте на привычных тратах</h2>
                    <p className="text-slate-300">
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
