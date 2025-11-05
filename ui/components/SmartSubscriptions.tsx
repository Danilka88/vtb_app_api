import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Subscription, Account } from '../types';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
});

const getDaysUntilPayment = (dateString: string): number => {
    const paymentDate = new Date(dateString);
    const today = new Date();
    // Reset time to start of the day for accurate day difference
    paymentDate.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);
    const diffTime = paymentDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export const SmartSubscriptions: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setSubscriptions(financialData.subscriptions);
            setLoading(false);
        };
        loadData();
    }, []);

    const handleToggleBlock = (subscriptionId: string) => {
        setSubscriptions(prevSubs =>
            prevSubs.map(sub =>
                sub.id === subscriptionId
                    ? { ...sub, status: sub.status === 'active' ? 'blocked' : 'active' }
                    : sub
            )
        );
    };

    const accountsMap = useMemo(() => {
        if (!data) return new Map<string, Account>();
        return new Map(data.accounts.map(acc => [acc.id, acc]));
    }, [data]);

    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Умное управление подписками</h1>
                        <p className="text-slate-400 mt-1">Возьмите подписки под контроль и избегайте лишних трат.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Никогда не платите за то, чем не пользуетесь</h2>
                    <p className="text-slate-300">
                        Сервис предупредит вас за 3 дня до списания денег за подписку. Если вы не планируете ей пользоваться, просто заблокируйте следующий платеж в один клик.
                    </p>
                </Card>

                <Card>
                    <div className="divide-y divide-slate-700/50">
                        {subscriptions.map(sub => {
                            const linkedAccount = accountsMap.get(sub.linkedAccountId);
                            const daysUntil = getDaysUntilPayment(sub.nextPaymentDate);
                            const isBlocked = sub.status === 'blocked';
                            const isDueSoon = daysUntil >= 0 && daysUntil <= 3 && !isBlocked;

                            return (
                                <div key={sub.id} className={`p-4 ${isDueSoon ? 'bg-amber-500/10' : ''}`}>
                                    <div className="flex flex-col sm:flex-row justify-between sm:items-center">
                                        <div>
                                            <p className="text-lg font-bold text-white">{sub.name}</p>
                                            {linkedAccount && (
                                                 <div className="flex items-center gap-2 text-sm text-slate-400 mt-1">
                                                    <span className="block w-1 h-4 rounded-full" style={{ backgroundColor: linkedAccount.brandColor }}></span>
                                                    <span>{linkedAccount.bankName} •••• {linkedAccount.last4}</span>
                                                </div>
                                            )}
                                        </div>
                                        <div className="mt-2 sm:mt-0 sm:text-right">
                                            <p className="text-xl font-semibold text-white">{currencyFormatter.format(sub.amount)}<span className="text-sm text-slate-400">/мес</span></p>
                                            <p className="text-sm text-slate-500">
                                                Следующее списание: {new Date(sub.nextPaymentDate).toLocaleDateString('ru-RU')}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="mt-3 flex flex-col sm:flex-row justify-between items-center gap-3">
                                        <div className="w-full sm:w-auto">
                                            {isBlocked && (
                                                <p className="text-sm font-semibold text-red-400">🔴 Списание заблокировано</p>
                                            )}
                                            {isDueSoon && (
                                                <p className="text-sm font-semibold text-amber-400">🟡 Списание через {daysUntil} {daysUntil === 1 ? 'день' : 'дня'}</p>
                                            )}
                                        </div>
                                        <button
                                            onClick={() => handleToggleBlock(sub.id)}
                                            className={`w-full sm:w-auto px-4 py-2 text-sm font-semibold rounded-lg transition ${
                                                isBlocked 
                                                ? 'bg-green-500/20 text-green-300 hover:bg-green-500/30' 
                                                : 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30'
                                            }`}
                                        >
                                            {isBlocked ? 'Разблокировать' : 'Заблокировать списание'}
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </Card>
            </div>
        </div>
    );
};
