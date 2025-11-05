import React from 'react';

export type ActiveView = 'dashboard' | 'cards' | 'payments' | 'history' | 'assistant' | 'night-safe' | 'cashback' | 'smart-pay' | 'smart-debiting' | 'smart-exchange' | 'smart-subscriptions' | 'smart-loan-payments' | 'subscription-marketplace' | 'trust-platform';

export interface NavItem {
  id: ActiveView;
  label: string;
  icon: React.ReactNode;
}

export interface Account {
  id: string;
  name: string;
  bankName: string;
  last4: string;
  balance: number;
  type: 'debit' | 'credit' | 'savings';
  brandColor: string;
}

export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: 'income' | 'expense';
  category: string;
}

export interface FinancialGoal {
  id: string;
  name: string;
  currentAmount: number;
  targetAmount: number;
}

export interface NightSafeData {
    enabled: boolean;
    includedAccountIds: string[];
    targetAccountId: string;
    stats: {
        yesterday: number;
        month: number;
        total: number;
    }
}

export interface SmartPayData {
    enabled: boolean;
    includedAccountIds: string[];
}

export interface CashbackCategory {
    bankName: string;
    categories: { [key: string]: number };
}

export interface SpecialOffer {
    id: string;
    partnerName: string;
    bankName: string;
    description: string;
    expiryDate: string;
    brandColor: string;
}

export interface ExchangeRate {
    bankName: string;
    from: 'RUB';
    to: 'USD' | 'EUR' | 'CNY';
    buy: number;  // Rate at which bank buys currency from you (for RUB)
    sell: number; // Rate at which bank sells currency to you (for RUB)
    promotion?: string;
}

export interface Subscription {
    id: string;
    name: string;
    amount: number;
    billingCycle: 'monthly' | 'yearly';
    nextPaymentDate: string;
    linkedAccountId: string;
    status: 'active' | 'blocked';
}

export interface Loan {
    id: string;
    name: string;
    bankName: string;
    remainingAmount: number;
    interestRate: number;
    monthlyPayment: number;
    nextPaymentDate: string;
    linkedAccountId: string;
}

export interface RefinancingOffer {
    id: string;
    bankName: string;
    newInterestRate: number;
    description: string;
    maxAmount: number;
    brandColor: string;
}

export interface MarketplaceSubscription {
  id: string;
  name: string;
  logoUrl: string; // Placeholder for logo
  cost: number;
  billingCycle: 'monthly' | 'yearly';
  benefits: string[];
  relatedMerchants: string[]; // Descriptions from transactions
  cashbackCategory: string; // To find the best card
}

export interface TrustIssue {
  id: string;
  bankName: string;
  accountId?: string;
  type: 'hidden_fee' | 'low_interest' | 'unused_perk' | 'negative_feedback' | 'rate_discrepancy';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  recommendation: string;
}

export interface RecommendedCardOffer {
  id: string;
  name: string;
  bankName: string;
  brandColor: string;
  benefits: string[];
  isCredit: boolean;
  cashbackRates: { [key: string]: number };
}


export interface FinancialData {
  netWorth: number;
  accounts: Account[];
  transactions: Transaction[];
  goals: FinancialGoal[];
  nightSafe: NightSafeData;
  smartPay: SmartPayData;
  cashbackCategories: CashbackCategory[];
  specialOffers: SpecialOffer[];
  exchangeRates: ExchangeRate[];
  subscriptions: Subscription[];
  loans: Loan[];
  refinancingOffers: RefinancingOffer[];
  marketplaceSubscriptions: MarketplaceSubscription[];
  trustIssues: TrustIssue[];
  recommendedCardOffers: RecommendedCardOffer[];
}