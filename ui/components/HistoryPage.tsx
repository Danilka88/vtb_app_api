import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Transaction } from '../types';

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
});

export const HistoryPage: React.FC = () => {
  const [data, setData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const financialData = await fetchFinancialData();
      setData(financialData);
      setLoading(false);
    };
    loadData();
  }, []);

  const filteredTransactions = useMemo(() => {
    if (!data) return [];
    if (!filter) return data.transactions;
    return data.transactions.filter(t => 
      t.description.toLowerCase().includes(filter.toLowerCase()) ||
      t.category.toLowerCase().includes(filter.toLowerCase())
    );
  }, [data, filter]);

  if (loading || !data) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">История операций</h1>

        <div className="mb-6">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Поиск по описанию или категории..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
          />
        </div>

        <Card>
          <div className="space-y-2">
            {filteredTransactions.map(t => (
              <div key={t.id} className="flex justify-between items-center p-4 hover:bg-slate-700/50 rounded-lg">
                <div>
                  <p className="font-medium text-white">{t.description}</p>
                  <p className="text-sm text-slate-400">{t.category} - {new Date(t.date).toLocaleDateString('ru-RU')}</p>
                </div>
                <p className={`font-semibold text-lg ${t.type === 'income' ? 'text-green-400' : 'text-slate-300'}`}>
                  {t.type === 'income' ? '+' : ''}{currencyFormatter.format(t.amount)}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
