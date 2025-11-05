import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, TrustIssue, Account } from '../types';
import { ShieldExclamationIcon } from '../constants';

const severityConfig = {
    high: {
        iconColor: 'text-red-400',
        bgColor: 'bg-red-500/10',
        borderColor: 'border-red-500/50',
        label: 'Высокий риск',
    },
    medium: {
        iconColor: 'text-amber-400',
        bgColor: 'bg-amber-500/10',
        borderColor: 'border-amber-500/50',
        label: 'Средний риск',
    },
    low: {
        iconColor: 'text-blue-400',
        bgColor: 'bg-blue-500/10',
        borderColor: 'border-blue-500/50',
        label: 'Низкий риск',
    },
};

const TrustIssueCard: React.FC<{ issue: TrustIssue; account?: Account }> = ({ issue, account }) => {
    const config = severityConfig[issue.severity];

    return (
        <Card className={`p-5 border-l-4 ${config.borderColor} ${config.bgColor}`}>
            <div className="flex items-start gap-4">
                <ShieldExclamationIcon className={`w-8 h-8 flex-shrink-0 ${config.iconColor}`} />
                <div className="flex-1">
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="font-bold text-white text-lg">{issue.title}</h3>
                            <p className="text-sm text-slate-400">{issue.bankName}{account ? ` • ${account.name}` : ''}</p>
                        </div>
                        <span className={`text-xs font-bold px-2 py-1 rounded-full ${config.bgColor} ${config.iconColor}`}>{config.label}</span>
                    </div>
                    <p className="text-slate-300 mt-2 text-sm">{issue.description}</p>
                    <div className="mt-3 pt-3 border-t border-slate-700/50">
                        <p className="text-sm font-semibold text-green-400">Рекомендация:</p>
                        <p className="text-slate-200 text-sm">{issue.recommendation}</p>
                    </div>
                </div>
            </div>
        </Card>
    );
};

export const TrustPlatform: React.FC = () => {
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
                        <h1 className="text-3xl font-bold text-white">Платформа доверия</h1>
                        <p className="text-slate-400 mt-1">Ваш личный AI-аудитор для защиты от финансовых потерь.</p>
                    </div>
                    <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Как мы защищаем ваши интересы</h2>
                    <p className="text-slate-300">
                        Наш AI-алгоритм непрерывно анализирует условия ваших банковских продуктов, сравнивает их с рынком и проверяет на наличие "подводных камней". Мы выявляем скрытые комиссии, невыгодные ставки и неиспользуемые льготы, чтобы вы всегда были уверены в своих финансовых решениях.
                    </p>
                </Card>
                
                <div className="space-y-4">
                    {data.trustIssues.length > 0 ? (
                        data.trustIssues
                            .sort((a, b) => {
                                const severityOrder = { high: 1, medium: 2, low: 3 };
                                return severityOrder[a.severity] - severityOrder[b.severity];
                            })
                            .map(issue => (
                                <TrustIssueCard key={issue.id} issue={issue} account={issue.accountId ? accountsMap.get(issue.accountId) : undefined} />
                            ))
                    ) : (
                        <Card className="p-10 text-center">
                            <h3 className="text-xl font-semibold text-white">Все в порядке!</h3>
                            <p className="text-slate-400 mt-2">На данный момент мы не обнаружили никаких потенциальных рисков или проблем по вашим счетам.</p>
                        </Card>
                    )}
                </div>

            </div>
        </div>
    );
};