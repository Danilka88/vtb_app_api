import { FinancialData, TrustIssue } from '../types';

// Расширяем и добавляем новые счета для более сложных сценариев
const ACCOUNTS = {
    abank_debit: {
        id: 'acc_tbank_debit',
        name: 'ABank Black',
        bankName: 'ABank',
        last4: '1111',
        balance: 28340.70, // Уменьшен баланс для демонстрации нехватки средств
        type: 'debit' as 'debit',
        brandColor: '#EF3124',
    },
    sbank_debit: {
        id: 'acc_sber_debit',
        name: 'SBank Карта',
        bankName: 'SBank',
        last4: '2222',
        balance: 41200.90,
        type: 'debit' as 'debit',
        brandColor: '#228B22',
    },
    abank_debit_2: {
        id: 'acc_alfa_debit',
        name: 'A-Карта',
        bankName: 'ABank',
        last4: '7777',
        balance: 15800.00,
        type: 'debit' as 'debit',
        brandColor: '#EF3124',
    },
    abank_credit: {
        id: 'acc_tbank_credit',
        name: 'Fly Airlines',
        bankName: 'ABank',
        last4: '3333',
        balance: -25000.00,
        type: 'credit' as 'credit',
        brandColor: '#00BFFF',
    },
    vbank_savings: {
        id: 'acc_vtb_savings',
        name: 'Сейф',
        bankName: 'VBank',
        last4: '4444',
        balance: 540100.00,
        type: 'savings' as 'savings',
        brandColor: '#0033A0',
    },
    sbank_savings: {
        id: 'acc_sber_savings',
        name: 'Накопительный',
        bankName: 'SBank',
        last4: '5555',
        balance: 210000.00,
        type: 'savings' as 'savings',
        brandColor: '#005522',
    },
};

const MOCK_DATA: FinancialData = {
    netWorth: Object.values(ACCOUNTS).reduce((sum, acc) => sum + acc.balance, 0),
    accounts: Object.values(ACCOUNTS),
    transactions: [
        { id: 't1', date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), description: 'Зарплата', amount: 120000, type: 'income', category: 'Зарплата' },
        { id: 't2', date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), description: 'Perekrestok', amount: -3450.50, type: 'expense', category: 'Супермаркеты' },
        { id: 't3', date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), description: 'Yandex.Go', amount: -450.00, type: 'expense', category: 'Такси' },
        { id: 't4', date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), description: 'Yandex.Plus', amount: -299.00, type: 'expense', category: 'Подписки' },
        { id: 't5', date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), description: 'Ресторан "Огонек"', amount: -5600.00, type: 'expense', category: 'Рестораны' },
        { id: 't6', date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), description: 'Lukoil', amount: -2500.00, type: 'expense', category: 'АЗС' },
        { id: 't7', date: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(), description: 'Ozon.ru', amount: -7800.00, type: 'expense', category: 'Покупки' },
        { id: 't8', date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), description: 'Перевод от Ивана', amount: 5000, type: 'income', category: 'Переводы' },
        { id: 't9', date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), description: 'Aeroflot', amount: -15300, type: 'expense', category: 'Путешествия' },
        { id: 't10', date: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(), description: 'Pyaterochka', amount: -1234.20, type: 'expense', category: 'Супермаркеты' },
        { id: 't11', date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(), description: 'KinoPoisk', amount: -299.00, type: 'expense', category: 'Подписки' },
        { id: 't12', date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(), description: 'Yandex.Go', amount: -560.00, type: 'expense', category: 'Такси' },
        { id: 't13', date: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(), description: 'Litres.ru', amount: -499.00, type: 'expense', category: 'Книги' },
        { id: 't14', date: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(), description: 'SberMarket', amount: -4200.00, type: 'expense', category: 'Доставка' },
        { id: 't15', date: new Date(Date.now() - 22 * 24 * 60 * 60 * 1000).toISOString(), description: 'VK Music', amount: -169.00, type: 'expense', category: 'Подписки' },
        { id: 't16', date: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(), description: 'Ресторан "White Rabbit"', amount: -12500.00, type: 'expense', category: 'Рестораны' },
        { id: 't17', date: new Date(Date.now() - 16 * 24 * 60 * 60 * 1000).toISOString(), description: 'Кафе "Шоколадница"', amount: -1200.00, type: 'expense', category: 'Рестораны' },
    ],
    goals: [
        { id: 'g1', name: 'Отпуск в Таиланде', currentAmount: 210000, targetAmount: 350000 },
        { id: 'g2', name: 'Новый ноутбук', currentAmount: 45000, targetAmount: 150000 },
    ],
    nightSafe: {
        enabled: true,
        includedAccountIds: [ACCOUNTS.abank_debit.id, ACCOUNTS.sbank_debit.id, ACCOUNTS.abank_debit_2.id],
        targetAccountId: ACCOUNTS.vbank_savings.id,
        stats: { yesterday: 120.54, month: 3450.12, total: 15230.88 },
    },
    smartPay: {
        enabled: true,
        includedAccountIds: [ACCOUNTS.abank_debit.id, ACCOUNTS.sbank_debit.id, ACCOUNTS.abank_debit_2.id, ACCOUNTS.abank_credit.id],
    },
    cashbackCategories: [
        { bankName: 'ABank', categories: { 'Рестораны': 5, 'АЗС': 3, 'Путешествия': 2, 'Супермаркеты': 3, 'Подписки': 10, 'Книги': 5, 'Такси': 5 } },
        { bankName: 'SBank', categories: { 'Супермаркеты': 2, 'Рестораны': 1, 'АЗС': 1, 'Доставка': 5 } },
    ],
    specialOffers: [
        { id: 'so1', partnerName: 'Ozon', bankName: 'ABank', description: 'Кэшбэк 10% на все покупки электроники в приложении Ozon', expiryDate: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(), brandColor: '#4f46e5' },
        { id: 'so2', partnerName: 'M.Video', bankName: 'SBank', description: 'Скидка 2000₽ при покупке от 20000₽ по SBank Карте', expiryDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(), brandColor: '#ef4444' },
    ],
    exchangeRates: [
        { bankName: 'ABank', from: 'RUB', to: 'USD', buy: 90.5, sell: 92.8, promotion: 'Лучший курс в приложении' },
        { bankName: 'SBank', from: 'RUB', to: 'USD', buy: 89.9, sell: 94.1 },
        { bankName: 'VBank', from: 'RUB', to: 'USD', buy: 90.1, sell: 93.5 },
        { bankName: 'ABank', from: 'RUB', to: 'USD', buy: 90.2, sell: 93.8 }, // Second offer from the same bank
        { bankName: 'ABank', from: 'RUB', to: 'EUR', buy: 98.2, sell: 101.5 },
        { bankName: 'SBank', from: 'RUB', to: 'EUR', buy: 97.8, sell: 102.8 },
        { bankName: 'VBank', from: 'RUB', to: 'EUR', buy: 98.0, sell: 100.9, promotion: 'Выгодный курс на ЕВРО' },
        { bankName: 'ABank', from: 'RUB', to: 'CNY', buy: 12.5, sell: 13.1 },
        { bankName: 'SBank', from: 'RUB', to: 'CNY', buy: 12.3, sell: 13.5 },
        { bankName: 'ABank', from: 'RUB', to: 'CNY', buy: 12.4, sell: 12.8, promotion: 'Лучший курс на Юань' },
    ],
    subscriptions: [
        { id: 'sub1', name: 'Yandex.Plus', amount: 299, billingCycle: 'monthly', nextPaymentDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.abank_debit.id, status: 'active' },
        { id: 'sub2', name: 'IVI', amount: 399, billingCycle: 'monthly', nextPaymentDate: new Date().toISOString(), linkedAccountId: ACCOUNTS.sbank_debit.id, status: 'active' },
        { id: 'sub3', name: 'VK Music', amount: 169, billingCycle: 'monthly', nextPaymentDate: new Date(Date.now() + 20 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.sbank_debit.id, status: 'blocked' },
        { id: 'sub4', name: 'Ozon Premium', amount: 1999, billingCycle: 'yearly', nextPaymentDate: new Date(new Date().setMonth(new Date().getMonth() + 5)).toISOString(), linkedAccountId: ACCOUNTS.abank_debit_2.id, status: 'active' },
        { id: 'sub5', name: 'ABank Pro', amount: 199, billingCycle: 'monthly', nextPaymentDate: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.abank_debit.id, status: 'active' },
    ],
    loans: [
        { id: 'loan1', name: 'Автокредит', bankName: 'SBank', remainingAmount: 850000, interestRate: 8.5, monthlyPayment: 25000, nextPaymentDate: new Date(Date.now() + 12 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.sbank_debit.id },
        { id: 'loan2', name: 'Ипотека', bankName: 'VBank', remainingAmount: 4500000, interestRate: 9.2, monthlyPayment: 42000, nextPaymentDate: new Date(Date.now() + 18 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.abank_debit.id },
        { id: 'loan3', name: 'Потребительский', bankName: 'ABank', remainingAmount: 250000, interestRate: 15.0, monthlyPayment: 10000, nextPaymentDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), linkedAccountId: ACCOUNTS.abank_debit_2.id },
    ],
    refinancingOffers: [
        { id: 'ref1', bankName: 'ABank', newInterestRate: 8.5, description: 'Лучшее предложение по рефинансированию ипотеки', maxAmount: 10000000, brandColor: '#EF3124' },
        { id: 'ref2', bankName: 'SBank', newInterestRate: 12.5, description: 'Рефинансируйте потребительские кредиты', maxAmount: 500000, brandColor: '#228B22' },
        { id: 'ref3', bankName: 'VBank', newInterestRate: 9.9, description: 'Рефинансируйте автокредит по сниженной ставке', maxAmount: 1500000, brandColor: '#0033A0' },
    ],
    marketplaceSubscriptions: [
        { id: 'ms1', name: 'Яндекс Плюс', logoUrl: '', cost: 299, billingCycle: 'monthly', benefits: ['Кинопоиск', 'Яндекс.Музыка', 'Баллы Плюса'], relatedMerchants: ['Yandex.Go', 'KinoPoisk'], cashbackCategory: 'Подписки' },
        { id: 'ms2', name: 'Ozon Premium', logoUrl: '', cost: 199, billingCycle: 'monthly', benefits: ['Бесплатная доставка', 'Ранний доступ к распродажам'], relatedMerchants: ['Ozon.ru'], cashbackCategory: 'Покупки' },
        { id: 'ms3', name: 'SberPrime', logoUrl: '', cost: 199, billingCycle: 'monthly', benefits: ['Okko', 'СберЗвук', 'Скидки на доставку'], relatedMerchants: ['SberMarket'], cashbackCategory: 'Подписки' },
        { id: 'ms4', name: 'Litres', logoUrl: '', cost: 399, billingCycle: 'monthly', benefits: ['Доступ к каталогу', 'Скидка на новинки'], relatedMerchants: ['Litres.ru'], cashbackCategory: 'Книги' },
    ],
    recommendedCardOffers: [
        {
            id: 'rec_card_1',
            name: 'ABank Premium',
            bankName: 'ABank',
            brandColor: '#333333',
            benefits: ['Повышенный кэшбэк в ресторанах', 'Бесплатная страховка в путешествиях', 'Консьерж-сервис 24/7'],
            isCredit: false,
            cashbackRates: { 'Рестораны': 10, 'Такси': 7, 'Супермаркеты': 2 }
        },
        {
            id: 'rec_card_2',
            name: 'SBank Travel',
            bankName: 'SBank',
            brandColor: '#FFD700',
            benefits: ['Мили за все покупки', 'Доступ в бизнес-залы аэропортов'],
            isCredit: true,
            cashbackRates: { 'Путешествия': 5, 'АЗС': 3 }
        }
    ],
    trustIssues: [
        {
            id: 'ti1',
            bankName: 'SBank',
            accountId: ACCOUNTS.sbank_savings.id,
            type: 'low_interest',
            severity: 'high',
            title: 'Низкая ставка по накопительному счету',
            description: 'Ваш "Накопительный" счет в SBank имеет ставку 7% годовых. В то же время, ваш счет "Сейф" в VBank предлагает 12%. Вы упускаете потенциальный доход.',
            recommendation: 'Рассмотрите возможность перевода средств со счета в SBank на счет в VBank, чтобы получать больший доход на остаток.',
        },
        {
            id: 'ti2',
            bankName: 'ABank',
            accountId: ACCOUNTS.abank_debit.id,
            type: 'hidden_fee',
            severity: 'medium',
            title: 'Риск комиссии за переводы',
            description: 'По вашей карте ABank Black переводы сверх 50 000 ₽/мес облагаются комиссией 1.5%. В этом месяце вы уже перевели 45 200 ₽.',
            recommendation: 'Для следующих крупных переводов используйте SBank Карту, где лимит выше, чтобы избежать комиссии.',
        },
        {
            id: 'ti3',
            bankName: 'ABank',
            accountId: ACCOUNTS.abank_credit.id,
            type: 'unused_perk',
            severity: 'low',
            title: 'Неиспользуемая льгота: Страховка',
            description: 'Мы заметили покупку авиабилетов. Ваша кредитная карта "Fly Airlines" включает бесплатную туристическую страховку для поездок за рубеж.',
            recommendation: 'Не забудьте активировать полис перед следующей поездкой в приложении ABank, чтобы не платить за страховку отдельно.',
        },
        {
            id: 'ti4',
            bankName: 'ABank',
            type: 'negative_feedback',
            severity: 'medium',
            title: 'Отзывы о работе поддержки',
            description: 'AI-анализ отзывов в сети за последний месяц показывает, что некоторые клиенты ABank сталкивались с трудностями при закрытии кредитных карт.',
            recommendation: 'Если планируете подобные операции, будьте готовы к возможным задержкам и сохраняйте все документы и переписку с банком.',
        }
    ] as TrustIssue[],
};

export const fetchFinancialData = async (): Promise<FinancialData> => {
    // Simulate API call delay
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(JSON.parse(JSON.stringify(MOCK_DATA))); // Deep copy to avoid mutation issues
        }, 500);
    });
};