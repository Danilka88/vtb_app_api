import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, Loan, Account, RefinancingOffer } from '../types';
import { ReceiptPercentIcon } from '../constants';

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

interface PaymentPlanResult {
    sufficient: boolean;
    shortfall?: number;
    plan?: WithdrawalStep[];
}

interface MatchedOffer {
    loan: Loan;
    offer: RefinancingOffer;
}

export const SmartLoanPayments: React.FC = () => {
    const [data, setData] = useState<FinancialData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedLoanId, setSelectedLoanId] = useState('');
    const [paymentPlan, setPaymentPlan] = useState<PaymentPlanResult | null>(null);
    
    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const financialData = await fetchFinancialData();
            setData(financialData);
            if (financialData.loans.length > 0) {
                setSelectedLoanId(financialData.loans[0].id);
            }
            setLoading(false);
        };
        loadData();
    }, []);

    const refinancingMatches = useMemo((): MatchedOffer[] => {
        if (!data) return [];
        const matches: MatchedOffer[] = [];
        for (const loan of data.loans) {
            for (const offer of data.refinancingOffers) {
                if (loan.bankName !== offer.bankName && loan.interestRate > offer.newInterestRate && loan.remainingAmount <= offer.maxAmount) {
                    matches.push({ loan, offer });
                }
            }
        }
        return matches;
    }, [data]);

    const handleCalculatePayment = () => {
        if (!data || !selectedLoanId) return;
        
        const loan = data.loans.find(l => l.id === selectedLoanId);
        const primaryAccount = data.accounts.find(acc => acc.id === loan?.linkedAccountId);
        
        if (!loan || !primaryAccount) return;

        if (primaryAccount.balance >= loan.monthlyPayment) {
            setPaymentPlan({ sufficient: true });
            return;
        }

        let shortfall = loan.monthlyPayment - primaryAccount.balance;
        const plan: WithdrawalStep[] = [{
            accountId: primaryAccount.id,
            accountName: primaryAccount.name,
            accountBank: primaryAccount.bankName,
            brandColor: primaryAccount.brandColor,
            amount: primaryAccount.balance,
            reason: 'Использовать доступный баланс с основного счета.'
        }];
        
        const sourceAccounts = data.accounts
            .filter(acc => acc.id !== primaryAccount.id && acc.type !== 'credit')
            .sort((a, b) => (a.type === 'debit' ? -1 : 1));

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
                    reason: `Покрыть остаток со счета "${account.name}"`
                });
                shortfall -= amountToTake;
            }
        }

        setPaymentPlan({
            sufficient: false,
            shortfall: loan.monthlyPayment - primaryAccount.balance,
            plan
        });
    };

    if (loading || !data) {
        return <div className="flex justify-center items-center h-screen"><Spinner /></div>;
    }
    
    const selectedLoan = data.loans.find(l => l.id === selectedLoanId);

    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                 <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Умные платежи по кредитам</h1>
                        <p className="text-slate-400 mt-1">Платите вовремя и ищите способы сэкономить.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Платите по кредитам с умом</h2>
                    <p className="text-slate-300">
                        Этот сервис помогает вам двумя способами: во-первых, он подбирает оптимальный способ оплаты ежемесячного взноса, если на основной карте не хватает денег. Во-вторых, он постоянно ищет более выгодные предложения по рефинансированию ваших кредитов в других банках.
                    </p>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Payment Optimization */}
                    <Card className="p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">Оптимизация ежемесячного платежа</h3>
                        {selectedLoan ? (
                        <>
                            <div className="mb-4">
                                <label htmlFor="loan" className="block text-sm font-medium text-slate-400 mb-1">Выберите кредит для оплаты</label>
                                <select 
                                    id="loan" 
                                    value={selectedLoanId} 
                                    onChange={(e) => { setSelectedLoanId(e.target.value); setPaymentPlan(null); }}
                                    className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                                >
                                    {data.loans.map(l => <option key={l.id} value={l.id}>{l.name} ({l.bankName})</option>)}
                                </select>
                            </div>
                            <div className="p-3 bg-slate-800 rounded-lg mb-4 text-center">
                                <p className="text-slate-400 text-sm">Ежемесячный платеж:</p>
                                <p className="text-white font-bold text-2xl">{currencyFormatter.format(selectedLoan.monthlyPayment)}</p>
                            </div>
                             <button
                                onClick={handleCalculatePayment}
                                className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
                            >
                                <ReceiptPercentIcon className="w-5 h-5" />
                                <span>Рассчитать план платежа</span>
                            </button>
                        </>
                        ) : <p className="text-slate-400">У вас нет активных кредитов.</p>}

                        {paymentPlan && (
                            <div className="mt-4">
                                {paymentPlan.sufficient ? (
                                    <p className="text-green-400 font-semibold text-center p-3 bg-green-500/10 rounded-lg">Средств на основном счете достаточно для платежа.</p>
                                ) : (
                                    <div className="space-y-2">
                                        <p className="text-amber-400 font-semibold">Недостаточно средств. План списания:</p>
                                        {paymentPlan.plan?.map(step => (
                                            <div key={step.accountId} className="p-2 bg-slate-700/50 rounded-lg flex justify-between items-center">
                                                <div className="flex items-center gap-2">
                                                    <span className="block w-1.5 h-5 rounded-full" style={{backgroundColor: step.brandColor}}></span>
                                                    <p className="text-white text-sm">{step.accountName}</p>
                                                </div>
                                                <p className="text-white font-semibold text-sm">{currencyFormatter.format(step.amount)}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </Card>

                    {/* Refinancing Opportunities */}
                    <Card className="p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">Возможности рефинансирования</h3>
                        {refinancingMatches.length > 0 ? (
                            <div className="space-y-4">
                                {refinancingMatches.map(({ loan, offer }) => {
                                    const monthlySaving = (loan.monthlyPayment - (loan.monthlyPayment * (offer.newInterestRate / loan.interestRate))).toFixed(0);
                                    return (
                                    <div key={offer.id} className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
                                        <p className="font-bold text-white">Рефинансирование для "{loan.name}"</p>
                                        <div className="flex justify-between items-center mt-2 text-sm">
                                            <p className="text-red-400">Текущая ставка: {loan.interestRate}%</p>
                                            <p className="text-green-400">Новая ставка: {offer.newInterestRate}%</p>
                                        </div>
                                        <div className="mt-3 p-3 bg-green-500/10 rounded-lg text-center">
                                            <p className="text-sm text-green-300">Примерная экономия в месяц:</p>
                                            <p className="text-lg font-bold text-white">{currencyFormatter.format(parseFloat(monthlySaving))}</p>
                                        </div>
                                        <button className="mt-3 w-full text-sm bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 rounded-lg transition">
                                            Узнать подробнее в {offer.bankName}
                                        </button>
                                    </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center h-full flex flex-col justify-center items-center">
                                <p className="text-slate-400">На данный момент выгодных предложений по рефинансированию не найдено.</p>
                            </div>
                        )}
                    </Card>
                </div>

            </div>
        </div>
    );
};