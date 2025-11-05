import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Transaction, Account, FinancialGoal, ActiveView } from '../types';
import { SparklesIcon } from '../constants';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const NetWorthCard: React.FC<{ netWorth: number }> = ({ netWorth }) => (
    <Card className="p-6 col-span-2 md:col-span-1 bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <h3 className="text-lg font-medium text-blue-200">Общий капитал</h3>
        <p className="text-4xl font-bold mt-2">{currencyFormatter.format(netWorth)}</p>
        <p className="text-sm mt-1 text-green-300">+2.5% за месяц</p>
    </Card>
);

const AccountsList: React.FC<{ accounts: Account[] }> = ({ accounts }) => (
    <Card className="p-6 col-span-2 md:col-span-1">
        <h3 className="text-lg font-semibold text-white mb-4">Счета</h3>
        <div className="space-y-4">
            {accounts.map(acc => (
                <div key={acc.id} className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <span className="block w-2 h-8 rounded-full" style={{ backgroundColor: acc.brandColor }}></span>
                        <div>
                            <p className="font-medium text-white">{acc.name}</p>
                            <p className="text-sm text-slate-400">{acc.bankName} •••• {acc.last4}</p>
                        </div>
                    </div>
                    <p className="font-semibold text-white">{currencyFormatter.format(acc.balance)}</p>
                </div>
            ))}
        </div>
    </Card>
);

const SpendingChart: React.FC<{ transactions: Transaction[] }> = ({ transactions }) => {
    const spendingData = transactions
        .filter(t => t.type === 'expense' && t.category !== 'Переводы')
        .reduce((acc, t) => {
            const category = t.category;
            const amount = Math.abs(t.amount);
            if (!acc[category]) {
                acc[category] = 0;
            }
            acc[category] += amount;
            return acc;
        }, {} as { [key: string]: number });

    const chartData = Object.entries(spendingData).map(([name, value]) => ({ name, value }));
    const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f97316', '#ec4899'];

    return (
        <Card className="p-6 col-span-2 md:col-span-1">
            <h3 className="text-lg font-semibold text-white mb-4">Траты по категориям</h3>
            <div style={{ width: '100%', height: 250 }}>
                <ResponsiveContainer>
                    <PieChart>
                        <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" labelLine={false}>
                            {chartData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                        </Pie>
                        <Tooltip formatter={(value: number) => currencyFormatter.format(value)} />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
};

const RecentTransactions: React.FC<{ transactions: Transaction[] }> = ({ transactions }) => (
    <Card className="p-6 col-span-2">
        <h3 className="text-lg font-semibold text-white mb-4">Последние операции</h3>
        <div className="space-y-3">
            {transactions.slice(0, 5).map(t => (
                <div key={t.id} className="flex justify-between items-center">
                    <div>
                        <p className="font-medium text-white">{t.description}</p>
                        <p className="text-sm text-slate-400">{t.category} - {new Date(t.date).toLocaleDateString('ru-RU')}</p>
                    </div>
                    <p className={`font-semibold ${t.type === 'income' ? 'text-green-400' : 'text-slate-300'}`}>
                        {t.type === 'income' ? '+' : ''}{currencyFormatter.format(t.amount)}
                    </p>
                </div>
            ))}
        </div>
    </Card>
);

const FinancialGoals: React.FC<{ goals: FinancialGoal[] }> = ({ goals }) => (
    <Card className="p-6 col-span-2">
        <h3 className="text-lg font-semibold text-white mb-4">Финансовые цели</h3>
        <div className="space-y-4">
            {goals.map(goal => {
                const progress = (goal.currentAmount / goal.targetAmount) * 100;
                return (
                    <div key={goal.id}>
                        <div className="flex justify-between mb-1">
                            <p className="font-medium text-white">{goal.name}</p>
                            <p className="text-sm text-slate-400">{currencyFormatter.format(goal.currentAmount)} / {currencyFormatter.format(goal.targetAmount)}</p>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2.5">
                            <div className="bg-gradient-to-r from-green-400 to-blue-500 h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
                        </div>
                    </div>
                );
            })}
        </div>
    </Card>
);

interface DashboardProps {
  setActiveView: (view: ActiveView) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ setActiveView }) => {
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

  if (loading || !data) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        <div className="col-span-1 md:col-span-2 lg:col-span-2">
          <Card className="p-6 flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-800">
            <div>
              <h2 className="text-2xl font-bold text-white">Финансовый Ассистент</h2>
              <p className="text-slate-400 mt-1">Задайте любой вопрос о ваших финансах и получите умный совет.</p>
            </div>
            <button
                onClick={() => setActiveView('assistant')}
                className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition shadow-lg w-full md:w-auto"
            >
                <SparklesIcon className="w-5 h-5" />
                <span>Спросить Ассистента</span>
            </button>
          </Card>
        </div>
        <NetWorthCard netWorth={data.netWorth} />
        <AccountsList accounts={data.accounts} />
        <SpendingChart transactions={data.transactions} />
        <RecentTransactions transactions={data.transactions} />
        <FinancialGoals goals={data.goals} />
    </div>
  );
};