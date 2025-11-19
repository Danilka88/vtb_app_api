
import React, { useState } from 'react';
import { Card } from './shared/Card';
import { Logo } from '../constants';

interface LoginPageProps {
  /** 
   * Callback to set the authenticated user ID in the parent app state.
   * In a real app, this would likely receive a JWT or session object.
   */
  onLogin: (userId: string) => void;
}

/**
 * Component: LoginPage
 * 
 * Description:
 * Serves as the entry point for the demonstration. 
 * Since the backend utilizes Client Credentials Flow (Client ID/Secret) for service-to-service auth,
 * this page simulates a user login to establish a 'user_id' context for the demo session.
 * 
 * API Interaction:
 * - Currently: None (Client-side validation only).
 * - Future/Production: POST /api/v1/auth/login -> returns Session/JWT.
 */
export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('team042-1');
  const [password, setPassword] = useState('g5IwpF35y8FYTrlN');
  const [error, setError] = useState('');

  // Hardcoded credentials for demonstration purposes
  const DEMO_PASSWORD = 'g5IwpF35y8FYTrlN';
  // Regex pattern validation for team username format (team042-X)
  const USERNAME_REGEX = /^team042-\d+$/;

  const handleLogin = () => {
    setError('');
    // Validate username format
    if (!USERNAME_REGEX.test(username)) {
      setError('Неверный формат имени пользователя. Ожидается "team042-X".');
      return;
    }
    // Validate password (exact match required)
    if (password !== DEMO_PASSWORD) {
      setError('Неверный пароль.');
      return;
    }
    // Successful login: Pass userId up to App.tsx
    onLogin(username);
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-slate-900 p-4">
      <Card className="p-8 w-full max-w-sm bg-slate-800 border-slate-700">
        <div className="flex justify-center items-center gap-2 mb-6">
          <Logo className="w-10 h-10" />
          <h1 className="text-2xl font-bold text-white">Мультибанк</h1>
        </div>
        <h2 className="text-xl text-center font-semibold text-white mb-6">Вход для демо-доступа</h2>
        <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-400 mb-1">
                Имя пользователя
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                placeholder="team042-1"
              />
            </div>
            <div>
              <label htmlFor="password" aria-label="password" className="block text-sm font-medium text-slate-400 mb-1">
                Пароль
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
              />
            </div>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
               <p className="text-sm text-center text-red-400">{error}</p>
            </div>
          )}
          <button
            type="submit"
            className="mt-6 w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-lg"
          >
            Войти
          </button>
        </form>
      </Card>
    </div>
  );
};
