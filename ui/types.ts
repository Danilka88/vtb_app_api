
import React from 'react';

/**
 * Defines the available views in the application.
 * Used for navigation state management within the single-page application.
 */
export type ActiveView = 'dashboard' | 'cards' | 'payments' | 'history' | 'assistant' | 'night-safe' | 'cashback' | 'smart-pay' | 'smart-debiting' | 'smart-exchange' | 'smart-subscriptions' | 'smart-loan-payments' | 'subscription-marketplace' | 'trust-platform' | 'connect-banks' | 'smart-budgeting' | 'financial-health';

/**
 * Structure for navigation items in the Sidebar and BottomNav.
 */
export interface NavItem {
  id: ActiveView;
  label: string;
  icon: React.ReactNode;
}

/**
 * Represents a bank account (checking, savings, credit card).
 * 
 * @api GET /api/v1/accounts
 */
export interface Account {
  /** Unique identifier for the account (UUID) */
  id: string;
  /** User-friendly name of the account (e.g., "Main Debit", "Vacation Fund") */
  name: string;
  /** Name of the bank holding the account (e.g., "VBank", "SBank") */
  bankName: string;
  /** Last 4 digits of the card or account number for display security */
  last4: string;
  /** 
   * Current available balance in the account currency (assumed RUB for this demo).
   * For credit cards, this is the available credit or remaining balance depending on context.
   */
  balance: number;
  /** 
   * Type of the account affecting logic in "Smart Debiting" and "Night Safe".
   * - 'debit': Liquid funds, prioritized for spending.
   * - 'credit': Borrowed funds, typically ignored for savings logic.
   * - 'savings': Interest-bearing, deprioritized for spending.
   */
  type: 'debit' | 'credit' | 'savings';
  /** Hex color code associated with the bank branding for UI consistency */
  brandColor: string;
}

/**
 * Represents a financial transaction.
 * 
 * @api GET /api/v1/transactions
 */
export interface Transaction {
  /** Unique identifier for the transaction */
  id: string;
  /** ISO 8601 date string */
  date: string;
  /** Description or merchant name (e.g., "Starbucks", "Salary") */
  description: string;
  /** 
   * Transaction amount. 
   * Positive values indicate income.
   * Negative values indicate expense.
   */
  amount: number;
  /** High-level type of transaction */
  type: 'income' | 'expense';
  /** 
   * Category for budgeting and analytics.
   * Used by: 'Smart Pay' (to determine cashback), 'CardsPage' (recommendations), 'Dashboard' (charts).
   */
  category: string;
}

/**
 * Represents a user's financial goal.
 * 
 * @api GET /api/v1/goals
 */
export interface FinancialGoal {
  id: string;
  name: string;
  currentAmount: number;
  targetAmount: number;
}

/**
 * Configuration and stats for the "Night Safe" feature.
 * This feature automates moving idle funds to a savings account overnight.
 * 
 * @api GET /api/v1/features/night-safe
 */
export interface NightSafeData {
    /** Is the feature currently active for the user? */
    enabled: boolean;
    /** List of Account IDs that participate in the sweep (source accounts) */
    includedAccountIds: string[];
    /** The Account ID where funds are moved to (destination account) */
    targetAccountId: string;
    /** Statistics on earnings to display value to the user */
    stats: {
        yesterday: number;
        month: number;
        total: number;
    }
}

/**
 * Configuration for "Smart Pay".
 * Automatically selects the best card for a purchase based on cashback.
 * 
 * @api GET /api/v1/features/smart-pay
 */
export interface SmartPayData {
    enabled: boolean;
    /** List of Account IDs included in the optimization logic */
    includedAccountIds: string[];
}

/**
 * Cashback rules for a specific bank.
 * Used to calculate the best card for payments (Smart Pay) and recommendations.
 * 
 * @api GET /api/v1/reference/cashback-categories
 */
export interface CashbackCategory {
    bankName: string;
    /** 
     * Map of Category Name -> Cashback Percentage.
     * Example: { "Restaurants": 5, "Fuel": 3 } 
     */
    categories: { [key: string]: number };
}

/**
 * Special marketing offers from partners.
 * Displayed in the "Cashback Radar" component.
 * 
 * @api GET /api/v1/offers/special
 */
export interface SpecialOffer {
    id: string;
    partnerName: string;
    bankName: string;
    description: string;
    expiryDate: string;
    brandColor: string;
}

/**
 * Exchange rates for currency conversion.
 * Used in "Smart Exchange" to compare rates across connected banks.
 * 
 * @api GET /api/v1/reference/exchange-rates
 */
export interface ExchangeRate {
    bankName: string;
    from: 'RUB';
    to: 'USD' | 'EUR' | 'CNY';
    /** Rate to buy foreign currency (Bank sells to user) */
    buy: number;
    /** Rate to sell foreign currency (Bank buys from user) */
    sell: number;
    /** Optional text for promotional rates (e.g., "Premium Client Rate") */
    promotion?: string;
}

/**
 * Represents a recurring subscription detected from transaction history.
 * 
 * @api GET /api/v1/subscriptions
 */
export interface Subscription {
    id: string;
    name: string;
    amount: number;
    billingCycle: 'monthly' | 'yearly';
    /** ISO 8601 date string of next estimated payment */
    nextPaymentDate: string;
    /** Account ID used for payment */
    linkedAccountId: string;
    /** 'blocked' status implies the bank will decline the next transaction from this merchant */
    status: 'active' | 'blocked';
}

/**
 * Represents a loan or mortgage.
 * 
 * @api GET /api/v1/loans
 */
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

/**
 * Offer to refinance a loan from a partner bank.
 * 
 * @api GET /api/v1/offers/refinancing
 */
export interface RefinancingOffer {
    id: string;
    bankName: string;
    newInterestRate: number;
    description: string;
    maxAmount: number;
    brandColor: string;
}

/**
 * A subscription service available in the marketplace.
 * 
 * @api GET /api/v1/marketplace/subscriptions
 */
export interface MarketplaceSubscription {
  id: string;
  name: string;
  logoUrl: string;
  cost: number;
  billingCycle: 'monthly' | 'yearly';
  benefits: string[];
  /** Merchant descriptors used to detect if user already uses this service via transaction history */
  relatedMerchants: string[];
  /** Used to recommend the best card for this subscription */
  cashbackCategory: string;
}

/**
 * An issue detected by the "Trust Platform" auditor algorithm.
 * 
 * @api GET /api/v1/trust-platform/issues
 */
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

/**
 * A recommended credit/debit card offer based on user spending analysis.
 * 
 * @api GET /api/v1/offers/cards
 */
export interface RecommendedCardOffer {
  id: string;
  name: string;
  bankName: string;
  brandColor: string;
  benefits: string[];
  isCredit: boolean;
  cashbackRates: { [key: string]: number };
}

/**
 * Represents a budget "envelope" category.
 */
export interface BudgetEnvelope {
    id: string;
    name: string;
    /** 'essentials' = 50%, 'wants' = 30%, 'savings' = 20% */
    type: 'essentials' | 'wants' | 'savings';
    allocatedAmount: number;
    spentAmount: number;
    forecastedAmount: number;
    color: string;
}

/**
 * Data for the AI Budgeting feature.
 * 
 * @api GET /api/v1/budgeting/plan
 */
export interface BudgetPlan {
    totalMonthlyIncome: number;
    /** Calculated "Safe to Spend" per day based on remaining discretionary funds */
    safeDailySpend: number;
    daysRemainingInMonth: number;
    envelopes: BudgetEnvelope[];
    insights: string[];
}

/**
 * Represents a single metric component of the overall financial health score.
 */
export interface HealthComponent {
    id: string;
    category: 'spending' | 'debt' | 'savings' | 'regularity';
    label: string;
    score: number;
    maxScore: number;
    status: 'excellent' | 'good' | 'fair' | 'poor';
    advice: string;
}

/**
 * Gamification badge awarded for financial achievements.
 */
export interface Badge {
    id: string;
    name: string;
    description: string;
    iconName: string; // simple string reference for icon mapping
    unlocked: boolean;
}

/**
 * Reward unlocked by improving financial health.
 */
export interface Reward {
    id: string;
    title: string;
    description: string;
    requiredScore: number;
    isLocked: boolean;
}

/**
 * Data structure for the "Financial Health" feature.
 * 
 * @api GET /api/v1/financial-health
 */
export interface FinancialHealth {
    totalScore: number; // 0-100
    components: HealthComponent[];
    badges: Badge[];
    rewards: Reward[];
}

/**
 * Aggregated object containing all financial data for the user.
 * This simulates the response from a "Backend-for-Frontend" (BFF) aggregator endpoint.
 * 
 * @api GET /api/v1/aggregator/dashboard
 */
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
  budgetPlan: BudgetPlan;
  financialHealth: FinancialHealth;
}
