import React, { useState, useEffect } from 'react';
import { Card } from './shared/Card';
import { Spinner } from './shared/Spinner';
import { fetchFinancialData } from '../services/financialService';
import { FinancialData, SpecialOffer } from '../types';
import { TagIcon } from '../constants';

const OfferCard: React.FC<{ offer: SpecialOffer }> = ({ offer }) => (
    <Card className="p-5 flex flex-col justify-between hover:shadow-blue-500/20 hover:border-blue-500 transition-all duration-300">
        <div>
            <div className="flex items-center gap-3 mb-3">
                 <span className="block w-2 h-8 rounded-full" style={{ backgroundColor: offer.brandColor }}></span>
                 <div>
                    <p className="font-bold text-white text-lg">{offer.partnerName}</p>
                    <p className="text-sm text-slate-400">от {offer.bankName}</p>
                 </div>
            </div>
            <p className="text-slate-200 mb-4">{offer.description}</p>
        </div>
        <div className="text-right">
            <p className="text-xs text-slate-500">Действует до: {new Date(offer.expiryDate).toLocaleDateString('ru-RU')}</p>
        </div>
    </Card>
);

export const CashbackRadar: React.FC = () => {
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
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Акции от партнеров</h1>
                        <p className="text-slate-400 mt-1">Лучшие временные предложения от ваших банков.</p>
                    </div>
                     <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full uppercase">Premium</div>
                </div>

                <Card className="p-6 mb-6 bg-slate-800">
                    <div className="flex items-center gap-4">
                        <TagIcon className="w-8 h-8 text-blue-400 flex-shrink-0" />
                        <div>
                            <h2 className="text-xl font-semibold text-white">Охотьтесь за выгодой!</h2>
                            <p className="text-slate-300 mt-1">
                                Здесь собраны уникальные акции с повышенным кэшбэком и специальные условия от партнеров ваших банков. Предложения ограничены по времени — не упустите свой шанс!
                            </p>
                        </div>
                    </div>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {data.specialOffers.map(offer => (
                        <OfferCard key={offer.id} offer={offer} />
                    ))}
                </div>
            </div>
        </div>
    );
};