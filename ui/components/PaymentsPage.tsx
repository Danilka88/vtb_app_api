import React from 'react';
import { Card } from './shared/Card';
import { PhoneIcon, QrCodeIcon, HomeModernIcon, GlobeAltIcon, HeartIcon, CogIcon } from '../constants';

interface PaymentOptionProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const PaymentOption: React.FC<PaymentOptionProps> = ({ icon, title, description }) => (
    <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-slate-700/50 transition-colors cursor-pointer">
        <div className="bg-slate-700 p-3 rounded-lg text-blue-400">
            {icon}
        </div>
        <div>
            <h3 className="font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400">{description}</p>
        </div>
    </div>
);


export const PaymentsPage: React.FC = () => {
    const paymentOptions = [
        { icon: <PhoneIcon className="w-6 h-6" />, title: 'Перевод по номеру', description: 'Контактам или на карту' },
        { icon: <QrCodeIcon className="w-6 h-6" />, title: 'Оплата по QR', description: 'Сканируйте и платите' },
        { icon: <HomeModernIcon className="w-6 h-6" />, title: 'Коммунальные услуги', description: 'ЖКХ, свет, газ, вода' },
        { icon: <GlobeAltIcon className="w-6 h-6" />, title: 'Интернет и ТВ', description: 'Оплата услуг провайдеров' },
        { icon: <HeartIcon className="w-6 h-6" />, title: 'Благотворительность', description: 'Помощь фондам и проектам' },
        { icon: <CogIcon className="w-6 h-6" />, title: 'Другие платежи', description: 'Налоги, штрафы, образование' },
    ];
    
    return (
        <div className="p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-white mb-6">Платежи и переводы</h1>
                <Card className="p-4 md:p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {paymentOptions.map(opt => (
                           <PaymentOption key={opt.title} {...opt} />
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
};
