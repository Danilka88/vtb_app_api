
import React, { useState, useEffect } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Account } from '../types';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const StatCard: React.FC<{ label: string; value: number; colorClass: string }> = ({ label, value, colorClass }) => (
    <Card className="p-4">
        <p className="text-sm text-slate-400">{label}</p>
        <p className={`text-2xl font-bold ${colorClass}`}>{currencyFormatter.format(value)}</p>
    </Card>
);

export const NightSafe: React.FC = () => {
  const [data, setData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEnabled, setIsEnabled] = useState(false);
  const [includedAccounts, setIncludedAccounts] = useState<Set<string>>(new Set());

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const financialData = await fetchFinancialData();
      setData(financialData);
      setIsEnabled(financialData.nightSafe.enabled);
      setIncludedAccounts(new Set(financialData.nightSafe.includedAccountIds));
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

  if (loading || !data) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }

  const targetAccount = data.accounts.find(acc => acc.id === data.nightSafe.targetAccountId);
  const totalBalanceToMove = data.accounts
    .filter(acc => includedAccounts.has(acc.id) && acc.id !== data.nightSafe.targetAccountId && acc.type !== 'credit')
    .reduce((sum, acc) => sum + acc.balance, 0);

  return (
    <div className="p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Ночной Сейф</h1>
                <p className="text-slate-400 mt-1">Заставьте ваши деньги работать, пока вы спите.</p>
            </div>
            <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
        </div>
        
        <Card className="p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-2">Как это работает?</h2>
            <p className="text-slate-300">
              Каждую ночь в 23:55 мы автоматически собираем остатки с выбранных вами счетов на один, где начисляется процент на остаток. Сразу после полуночи, в 00:05, мы возвращаем все деньги обратно. Вы получаете доход, не меняя своих привычек.
            </p>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <StatCard label="Заработано вчера" value={data.nightSafe.stats.yesterday} colorClass="text-green-400" />
            <StatCard label="Заработано за месяц" value={data.nightSafe.stats.month} colorClass="text-blue-400" />
            <StatCard label="Заработано всего" value={data.nightSafe.stats.total} colorClass="text-purple-400" />
        </div>

        <Card className="p-6">
            <div className="flex justify-between items-center pb-4 border-b border-slate-700/50">
                <div>
                    <h3 className="text-lg font-semibold text-white">Статус сервиса</h3>
                    <p className="text-sm text-slate-400">Включите, чтобы начать зарабатывать.</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" checked={isEnabled} onChange={() => setIsEnabled(!isEnabled)} className="sr-only peer" />
                    <div className="w-14 h-8 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-green-500"></div>
                </label>
            </div>
            
            <div className={`mt-4 space-y-3 ${!isEnabled ? 'opacity-50 pointer-events-none' : ''}`}>
                 <h3 className="text-lg font-semibold text-white pt-2">Участвующие счета</h3>
                 <div className="p-3 rounded-lg bg-slate-700/50">
                    <p className="text-sm font-medium text-white">Целевой счет для начислений:</p>
                    <p className="text-sm text-slate-300">{targetAccount?.name} ({targetAccount?.bankName})</p>
                 </div>
                 {data.accounts.filter(acc => acc.id !== targetAccount?.id && acc.type !== 'credit').map(account => (
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
                            <div className="w-11 h-6 bg-slate-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                     </div>
                 ))}
                 <div className="pt-4 text-center text-slate-300">
                     <p>К переводу сегодня в 23:55: <span className="font-bold text-white">{currencyFormatter.format(totalBalanceToMove)}</span></p>
                 </div>
            </div>
        </Card>
      </div>
    </div>
  );
};
