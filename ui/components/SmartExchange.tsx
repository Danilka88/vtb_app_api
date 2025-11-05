import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, ExchangeRate } from '../types';
import { ScaleIcon } from '../constants';

type Currency = 'RUB' | 'USD' | 'EUR' | 'CNY';

interface RateOption extends ExchangeRate {
    result: number;
}

interface CalculationResult {
    options: RateOption[];
}

const currencySymbols: { [key in Currency]: string } = {
    RUB: '₽',
    USD: '$',
    EUR: '€',
    CNY: '¥',
};

export const SmartExchange: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [loading, setLoading] = useState(true);
    const [amount, setAmount] = useState('10000');
    const [toCurrency, setToCurrency] = useState<Currency>('USD');
    const [result, setResult] = useState<CalculationResult | null>(null);

    const fromCurrency: Currency = 'RUB';

    const availableCurrencies = useMemo(() => {
        if (!data) return [];
        const currencies = data.exchangeRates.map(rate => rate.to);
        return [...new Set(currencies)];
    }, [data]);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            setLoading(false);
        };
        loadData();
    }, []);

    const handleCalculate = () => {
        if (!data || !amount) return;

        const numericAmount = parseFloat(amount);
        const relevantRates = data.exchangeRates.filter(
            rate => rate.from === fromCurrency && rate.to === toCurrency
        );

        const options = relevantRates.map(rate => ({
            ...rate,
            result: numericAmount / rate.sell,
        })).sort((a, b) => b.result - a.result); // Sort descending by result

        setResult({ options });
    };

    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }
    
    const getBankColor = (bankName: string) => {
        const account = data.accounts.find(acc => acc.bankName === bankName);
        return account?.brandColor || '#64748b'; // default slate color
    }

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Умный Обмен</h1>
                        <p className="text-slate-400 mt-1">Найдите самый выгодный курс для обмена валюты.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Обменивайте с максимальной выгодой</h2>
                    <p className="text-slate-300">
                        Сервис анализирует курсы всех ваших банков и находит лучшее предложение для покупки валюты, включая специальные и промо-курсы.
                    </p>
                </Card>

                <Card className="p-6 mb-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Калькулятор обмена</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                        <div>
                            <label htmlFor="amount" className="block text-sm font-medium text-slate-400 mb-1">Сумма в {currencySymbols[fromCurrency]}</label>
                            <input
                                id="amount"
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                placeholder="10000"
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                            />
                        </div>
                        <div>
                            <label htmlFor="toCurrency" className="block text-sm font-medium text-slate-400 mb-1">Хочу купить</label>
                            <select
                                id="toCurrency"
                                value={toCurrency}
                                onChange={(e) => setToCurrency(e.target.value as Currency)}
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                            >
                                {availableCurrencies.map(curr => <option key={curr} value={curr}>{curr}</option>)}
                            </select>
                        </div>
                    </div>
                    <button
                        onClick={handleCalculate}
                        className="mt-4 w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
                    >
                        <ScaleIcon className="w-5 h-5" />
                        <span>Найти лучший курс</span>
                    </button>
                </Card>
                
                {result && result.options.length > 0 && (
                    <Card className="p-6">
                        <h3 className="text-xl font-bold text-white mb-4">Результаты расчета</h3>
                        <div className="space-y-4">
                            {/* Best Offer */}
                            <div className="p-4 rounded-lg bg-slate-900/50 border-2 border-green-500">
                                <p className="text-sm font-bold text-green-400 mb-2">ЛУЧШЕЕ ПРЕДЛОЖЕНИЕ</p>
                                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
                                    <div className="flex items-center gap-3 mb-2 sm:mb-0">
                                        <span className="block w-2 h-8 rounded-full" style={{ backgroundColor: getBankColor(result.options[0].bankName) }}></span>
                                        <div>
                                            <p className="font-bold text-white text-lg">{result.options[0].bankName}</p>
                                            <p className="text-sm text-slate-400">Курс: {result.options[0].sell} {currencySymbols[fromCurrency]}</p>
                                        </div>
                                    </div>
                                    <div className="text-left sm:text-right">
                                        <p className="text-sm text-slate-300">Вы получите:</p>
                                        <p className="text-2xl font-bold text-white">
                                            {result.options[0].result.toFixed(2)} {currencySymbols[toCurrency]}
                                        </p>
                                    </div>
                                </div>
                                {result.options[0].promotion && (
                                    <div className="mt-3 p-2 text-center text-sm bg-blue-500/20 text-blue-300 rounded-md">
                                        {result.options[0].promotion}
                                    </div>
                                )}
                            </div>
                            
                            {/* Other Options */}
                            {result.options.length > 1 && (
                                <div>
                                    <h4 className="font-semibold text-slate-300 mt-6 mb-2">Другие варианты:</h4>
                                    <div className="space-y-3">
                                        {result.options.slice(1).map(option => {
                                            const saving = result.options[0].result - option.result;
                                            return (
                                                <div key={option.bankName} className="p-3 rounded-lg bg-slate-800 flex justify-between items-center">
                                                    <div className="flex items-center gap-3">
                                                         <span className="block w-1.5 h-6 rounded-full" style={{ backgroundColor: getBankColor(option.bankName) }}></span>
                                                         <div>
                                                             <p className="font-semibold text-white">{option.bankName}</p>
                                                             <p className="text-xs text-slate-500">Курс: {option.sell}</p>
                                                         </div>
                                                    </div>
                                                    <div>
                                                        <p className="font-semibold text-white">{option.result.toFixed(2)} {currencySymbols[toCurrency]}</p>
                                                        <p className="text-xs text-red-400 text-right">-{saving.toFixed(2)} {currencySymbols[toCurrency]}</p>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    </Card>
                )}

                 {result && result.options.length === 0 && (
                    <Card className="p-6 text-center">
                        <p className="text-slate-400">Не найдено вариантов для обмена по заданным валютам.</p>
                    </Card>
                 )}
            </div>
        </div>
    );
};