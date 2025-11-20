
import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { Dashboard } from './components/Dashboard';
import { Assistant } from './components/Assistant';
import { NightSafe } from './components/NightSafe';
import { CashbackRadar } from './components/CashbackRadar';
import { VBankPay } from './components/VBankPay';
import { CardsPage } from './components/CardsPage';
import { PaymentsPage } from './components/PaymentsPage';
import { HistoryPage } from './components/HistoryPage';
import { SmartDebiting } from './components/SmartDebiting';
import { SmartExchange } from './components/SmartExchange';
import { SmartSubscriptions } from './components/SmartSubscriptions';
import { SmartLoanPayments } from './components/SmartLoanPayments';
import { SubscriptionMarketplace } from './components/SubscriptionMarketplace';
import { TrustPlatform } from './components/TrustPlatform';
import { SmartBudgeting } from './components/SmartBudgeting';
import { FinancialHealthPage } from './components/FinancialHealth';
import { LoginPage } from './components/LoginPage';
import { ConnectBanksPage } from './components/ConnectBanksPage';
import { ActiveView, NavItem } from './types';
import { HomeIcon, CreditCardIcon, ArrowsRightLeftIcon, ClockIcon, ShieldCheckIcon, FireIcon, BoltIcon, SparklesIcon, LightBulbIcon, ScaleIcon, BellSlashIcon, ReceiptPercentIcon, BuildingStorefrontIcon, ShieldExclamationIcon, KeyIcon, CalculatorIcon, TrophyIcon } from './constants';

// Navigation configuration for Sidebar and BottomNav
const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Главная', icon: <HomeIcon className="w-6 h-6" /> },
  { id: 'connect-banks', label: 'Подключить банки', icon: <KeyIcon className="w-6 h-6" /> },
  { id: 'financial-health', label: 'Фин. Здоровье', icon: <TrophyIcon className="w-6 h-6" /> },
  { id: 'smart-budgeting', label: 'AI Бюджет', icon: <CalculatorIcon className="w-6 h-6" /> },
  { id: 'cards', label: 'Карты', icon: <CreditCardIcon className="w-6 h-6" /> },
  { id: 'payments', label: 'Платежи', icon: <ArrowsRightLeftIcon className="w-6 h-6" /> },
  { id: 'history', label: 'История', icon: <ClockIcon className="w-6 h-6" /> },
  { id: 'assistant', label: 'Ассистент', icon: <SparklesIcon className="w-6 h-6" /> },
  { id: 'smart-subscriptions', label: 'Подписки', icon: <BellSlashIcon className="w-6 h-6" /> },
  { id: 'smart-loan-payments', label: 'Кредиты', icon: <ReceiptPercentIcon className="w-6 h-6" /> },
  { id: 'subscription-marketplace', label: 'Маркетплейс', icon: <BuildingStorefrontIcon className="w-6 h-6" /> },
  { id: 'trust-platform', label: 'Платформа доверия', icon: <ShieldExclamationIcon className="w-6 h-6" /> },
  { id: 'night-safe', label: 'Ночной сейф', icon: <ShieldCheckIcon className="w-6 h-6" /> },
  { id: 'cashback', label: 'Акции', icon: <FireIcon className="w-6 h-6" /> },
  { id: 'smart-pay', label: 'Умная оплата', icon: <BoltIcon className="w-6 h-6" /> },
  { id: 'smart-debiting', label: 'Умное списание', icon: <LightBulbIcon className="w-6 h-6" /> },
  { id: 'smart-exchange', label: 'Умный Обмен', icon: <ScaleIcon className="w-6 h-6" /> },
];

/**
 * Component: App
 * 
 * Description:
 * The root component serving as the main layout container and router.
 * 
 * Responsibilities:
 * 1. Authentication Guard: Checks for `userId`. If missing, renders `LoginPage`.
 * 2. Navigation State: Manages `activeView` to switch between functional components.
 * 3. Layout: Renders Sidebar (Desktop), Header, BottomNav (Mobile), and Content Area.
 */
function App() {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard');
  const [userId, setUserId] = useState<string | null>(null);

  const handleLogin = (id: string) => {
    setUserId(id);
    // Redirect to 'connect-banks' page immediately after login
    setActiveView('connect-banks');
  };

  // Authentication Guard
  // If no user is logged in, show the Login Page.
  // In a real app, this would check a persistent session or JWT.
  if (!userId) {
    return <LoginPage onLogin={handleLogin} />;
  }

  /**
   * Renders the active component based on the state.
   * This serves as a client-side router replacement for demonstration simplicity.
   */
  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard setActiveView={setActiveView} />;
      case 'connect-banks':
        return <ConnectBanksPage userId={userId} />;
      case 'smart-budgeting':
        return <SmartBudgeting />;
      case 'financial-health':
        return <FinancialHealthPage />;
      case 'assistant':
        return <Assistant />;
      case 'night-safe':
        return <NightSafe />;
      case 'cashback':
          return <CashbackRadar />;
      case 'smart-pay':
          return <VBankPay />;
      case 'smart-debiting':
          return <SmartDebiting />;
      case 'smart-exchange':
          return <SmartExchange />;
      case 'smart-subscriptions':
          return <SmartSubscriptions />;
      case 'smart-loan-payments':
          return <SmartLoanPayments />;
      case 'subscription-marketplace':
          return <SubscriptionMarketplace />;
      case 'trust-platform':
          return <TrustPlatform />;
      case 'cards':
        return <CardsPage />;
      case 'payments':
        return <PaymentsPage />;
      case 'history':
        return <HistoryPage />;
      default:
        return <Dashboard setActiveView={setActiveView} />;
    }
  };

  return (
    <div className="bg-slate-900 min-h-screen font-sans text-slate-300">
      <Sidebar navItems={navItems} activeView={activeView} setActiveView={setActiveView} />
      <div className="lg:pl-64">
        <Header />
        <main className="pb-20 lg:pb-0">
          {renderContent()}
        </main>
      </div>
      <BottomNav navItems={navItems} activeView={activeView} setActiveView={setActiveView} />
    </div>
  );
}

export default App;
