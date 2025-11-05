
import React, { useState, useEffect } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Account } from '../types';
import { LightBulbIcon } from '../constants';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
});

interface WithdrawalStep {
    accountId: string;
    accountName: string;
    accountBank: string;
    brandColor: string;
    amount: number;
    reason: string;
}

interface CalculationResult {
    sufficient: boolean;
    shortfall?: number;
    plan?: WithdrawalStep[];
}

export const SmartDebiting: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [loading, setLoading] = useState(true);
    const [purchaseAmount, setPurchaseAmount] = useState('250000');
    const [primaryAccountId, setPrimaryAccountId] = useState('');
    const [result, setResult] = useState<CalculationResult | null>(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            if (financialData.accounts.length > 0) {
                setPrimaryAccountId(financialData.accounts[0].id);
            }
            setLoading(false);
        };
        loadData();
    }, []);

    const handleCalculate = () => {
        if (!data || !primaryAccountId || !purchaseAmount) return;

        const amount = parseFloat(purchaseAmount);
        const primaryAccount = data.accounts.find(acc => acc.id === primaryAccountId);
        if (!primaryAccount) return;

        if (primaryAccount.balance >= amount) {
            setResult({ sufficient: true });
            return;
        }
        
        let shortfall = amount - primaryAccount.balance;
        const plan: WithdrawalStep[] = [{
            accountId: primaryAccount.id,
            accountName: primaryAccount.name,
            accountBank: primaryAccount.bankName,
            brandColor: primaryAccount.brandColor,
            amount: primaryAccount.balance,
            reason: 'Использовать весь доступный баланс с основного счета.'
        }];
        
        const accountPriority = { 'debit': 1, 'savings': 2 };
        const sourceAccounts = data.accounts
            .filter(acc => acc.id !== primaryAccountId && acc.type !== 'credit')
            .sort((a, b) => (accountPriority[a.type] || 99) - (accountPriority[b.type] || 99));

        for (const account of sourceAccounts) {
            if (shortfall <= 0) break;
            
            const amountToTake = Math.min(account.balance, shortfall);
            if (amountToTake > 0) {
                plan.push({
                    accountId: account.id,
                    accountName: account.name,
                    accountBank: account.bankName,
                    brandColor: account.brandColor,
                    amount: amountToTake,
                    reason: account.type === 'debit' 
                        ? 'Покрыть остаток с другого дебетового счета, чтобы не трогать накопления.'
                        : 'Использовать средства с накопительного счета.'
                });
                shortfall -= amountToTake;
            }
        }
        
        setResult({
            sufficient: false,
            shortfall: amount - primaryAccount.balance,
            plan
        });
    };

    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Умное списание</h1>
                        <p className="text-slate-400 mt-1">Не хватило денег на карте? Мы подскажем, как совершить покупку с минимальными потерями.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Как это работает?</h2>
                    <p className="text-slate-300">
                        Если на выбранной карте не хватает средств для крупной покупки, наш сервис автоматически рассчитает самый выгодный способ покрыть разницу. Он в первую очередь использует другие ваши дебетовые счета и лишь затем — накопительные, чтобы вы не теряли доход по вкладам.
                    </p>
                </Card>
                
                <Card className="p-6 mb-6">
                     <h3 className="text-lg font-semibold text-white mb-4">Симулятор покупки</h3>
                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                        <div>
                            <label htmlFor="amount" className="block text-sm font-medium text-slate-400 mb-1">Сумма покупки, ₽</label>
                            <input
                                id="amount"
                                type="number"
                                value={purchaseAmount}
                                onChange={(e) => setPurchaseAmount(e.target.value)}
                                placeholder="Например, 250000"
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                            />
                        </div>
                        <div>
                            <label htmlFor="account" className="block text-sm font-medium text-slate-400 mb-1">Основной счет для оплаты</label>
                             <select 
                                id="account" 
                                value={primaryAccountId} 
                                onChange={(e) => setPrimaryAccountId(e.target.value)} 
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                             >
                                {data.accounts.filter(a => a.type !== 'credit').map(acc => <option key={acc.id} value={acc.id}>{acc.name} ({acc.bankName})</option>)}
                             </select>
                        </div>
                     </div>
                     <button
                        onClick={handleCalculate}
                        className="mt-4 w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
                    >
                        <LightBulbIcon className="w-5 h-5" />
                        <span>Рассчитать оптимальный план</span>
                    </button>
                </Card>

                {result && (
                    <Card className="p-6">
                        {result.sufficient ? (
                            <div className="text-center">
                                <h3 className="text-xl font-bold text-green-400">Средств достаточно!</h3>
                                <p className="text-slate-300 mt-2">На выбранном счете достаточно денег для совершения этой покупки.</p>
                            </div>
                        ) : (
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">Оптимальный план списания</h3>
                                <p className="text-slate-400 mb-4">Для покупки не хватает <span className="font-semibold text-amber-400">{currencyFormatter.format(result.shortfall || 0)}</span>. Вот как мы предлагаем покрыть разницу:</p>
                                <div className="space-y-3">
                                    {result.plan?.map((step, index) => (
                                        <div key={step.accountId} className="p-4 rounded-lg bg-slate-800 border border-slate-700 flex items-start gap-4">
                                            <div className="text-lg font-bold text-blue-400">#{index + 1}</div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="block w-1.5 h-5 rounded-full" style={{ backgroundColor: step.brandColor }}></span>
                                                    <p className="font-semibold text-white">{step.accountName} <span className="text-sm text-slate-400">({step.accountBank})</span></p>
                                                </div>
                                                <p className="text-sm text-slate-300 mt-1">{step.reason}</p>
                                            </div>
                                            <p className="font-semibold text-lg text-white whitespace-nowrap">{currencyFormatter.format(step.amount)}</p>
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between items-center">
                                    <p className="font-bold text-white text-lg">Итого к списанию:</p>
                                    <p className="font-bold text-white text-xl">{currencyFormatter.format(parseFloat(purchaseAmount))}</p>
                                </div>
                            </div>
                        )}
                    </Card>
                )}
            </div>
        </div>
    );
};
