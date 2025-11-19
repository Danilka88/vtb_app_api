
import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Account, RecommendedCardOffer } from '../types';
import { Logo } from '../constants';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  minimumFractionDigits: 0,
});

const BankCard: React.FC<{ account: Account }> = ({ account }) => {
    const isCredit = account.type === 'credit';
    const cardBg = isCredit ? 'bg-slate-700' : 'bg-blue-600';

    return (
        <div className={`relative aspect-[1.586] w-full max-w-sm rounded-xl text-white shadow-2xl p-6 flex flex-col justify-between ${cardBg}`}>
            <div>
                <div className="flex justify-between items-start">
                    <span className="font-semibold text-lg">{account.bankName}</span>
                    <Logo />
                </div>
                <div className="mt-6">
                    <span className="text-sm text-slate-300">Баланс</span>
                    <p className="text-3xl font-bold tracking-wider">{new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(account.balance)}</p>
                </div>
            </div>
            <div>
                <p className="font-mono text-lg tracking-widest">•••• •••• •••• {account.last4}</p>
                <div className="flex justify-between items-end mt-2">
                    <p className="uppercase text-sm">{account.name}</p>
                    <p className="text-sm font-semibold">{isCredit ? 'Кредитная карта' : 'Дебетовая карта'}</p>
                </div>
            </div>
        </div>
    );
};

const RecommendedCard: React.FC<{ recommendation: { offer: RecommendedCardOffer; topCategoryName: string; potentialSaving: number; } }> = ({ recommendation }) => {
    const { offer, topCategoryName, potentialSaving } = recommendation;
    return (
        <div className="lg:col-span-3 md:col-span-2 mt-8">
            <Card className="p-6 bg-gradient-to-r from-purple-600/30 to-blue-600/30 border-purple-500">
                <h2 className="text-2xl font-bold text-white mb-4">Для вас есть рекомендация!</h2>
                <div className="flex flex-col md:flex-row gap-6">
                    <div className="flex-shrink-0 mx-auto">
                        <div className={`relative aspect-[1.586] w-64 rounded-xl text-white shadow-2xl p-4 flex flex-col justify-between`} style={{backgroundColor: offer.brandColor}}>
                            <div>
                                <div className="flex justify-between items-start">
                                    <span className="font-semibold">{offer.bankName}</span>
                                    <Logo />
                                </div>
                                <p className="mt-8 font-semibold text-lg">{offer.name}</p>
                            </div>
                            <p className="uppercase text-xs">{offer.isCredit ? 'Кредитная карта' : 'Дебетовая карта'}</p>
                        </div>
                    </div>
                    <div>
                        <p className="text-slate-300 mb-3">
                            Мы проанализировали ваши траты и заметили, что вы часто совершаете покупки в категории <strong className="text-white">"{topCategoryName}"</strong>.
                        </p>
                        <p className="text-slate-200 font-semibold text-lg">
                             С картой <strong className="text-white">"{offer.name}"</strong> вы могли бы получать <strong className="text-green-400">{offer.cashbackRates[topCategoryName]}% кэшбэка</strong> и экономить дополнительно до <strong className="text-green-400">{currencyFormatter.format(potentialSaving)}</strong> в месяц.
                        </p>
                        <ul className="list-disc list-inside text-slate-300 space-y-1 mt-4 text-sm">
                            {offer.benefits.map(b => <li key={b}>{b}</li>)}
                        </ul>
                        <button className="mt-6 w-full md:w-auto bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 transition">
                            Оформить карту
                        </button>
                    </div>
                </div>
            </Card>
        </div>
    );
};


export const CardsPage: React.FC = () => {
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
  
  const recommendation = useMemo(() => {
    if (!data || !data.transactions || !data.recommendedCardOffers) return null;

    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);

    const spendingByCategory = data.transactions
        .filter(t => t.type === 'expense' && new Date(t.date) > oneMonthAgo)
        .reduce<Record<string, number>>((acc, t) => {
            if (!acc[t.category]) {
                acc[t.category] = 0;
            }
            acc[t.category] += Math.abs(t.amount);
            return acc;
        }, {});

    if (Object.keys(spendingByCategory).length === 0) return null;
    
    const sortedCategories = Object.entries(spendingByCategory).sort((a: [string, number], b: [string, number]) => b[1] - a[1]);
    const topCategory = sortedCategories[0];

    if (!topCategory) return null;

    const [topCategoryName, topCategorySpent] = topCategory;

    let currentUserBestRate = 0;
    data.accounts
        .filter(acc => acc.type === 'debit' || acc.type === 'credit')
        .forEach(account => {
            const bankCashback = data.cashbackCategories.find(c => c.bankName === account.bankName);
            const rate = bankCashback?.categories[topCategoryName] || 0;
            if (rate > currentUserBestRate) {
                currentUserBestRate = rate;
            }
        });

    let bestOffer: RecommendedCardOffer | null = null;
    let bestOfferRate = currentUserBestRate;

    for (const offer of data.recommendedCardOffers) {
        const offerRate = offer.cashbackRates[topCategoryName] || 0;
        if (offerRate > bestOfferRate) {
            bestOfferRate = offerRate;
            bestOffer = offer;
        }
    }

    if (bestOffer) {
        const potentialSaving = (topCategorySpent as number) * ((bestOfferRate - currentUserBestRate) / 100);
        if (potentialSaving > 100) { 
            return {
                offer: bestOffer,
                topCategoryName,
                potentialSaving
            };
        }
    }

    return null;
  }, [data]);

  if (loading || !data) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }
  
  const cards = data.accounts.filter(acc => acc.type === 'debit' || acc.type === 'credit');

  return (
    <div className="p-4 md:p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Ваши карты</h1>
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
         {cards.map(account => (
            <BankCard key={account.id} account={account} />
         ))}
         <Card className="flex flex-col items-center justify-center min-h-[220px] border-dashed border-2 border-slate-600 hover:border-blue-500 hover:bg-slate-700/50 transition cursor-pointer">
            <p className="text-blue-400 text-lg font-semibold">+ Добавить новую карту</p>
            <p className="text-slate-400 mt-1 text-sm">или привязать счет другого банка</p>
         </Card>
         {recommendation && <RecommendedCard recommendation={recommendation} />}
      </div>
    </div>
  );
};
