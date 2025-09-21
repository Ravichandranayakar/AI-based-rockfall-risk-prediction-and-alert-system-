import React, { useState } from 'react';
import { AlertTriangle, User, Lock, Eye, EyeOff, Shield, Zap, Mountain, Activity } from 'lucide-react';

const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted with:', { username, password });
    setIsLoading(true);
    setError('');

    // Simple validation
    if (!username || !password) {
      console.log('Validation failed: missing username or password');
      setError('Please enter both username and password');
      setIsLoading(false);
      return;
    }

    // Demo credentials (in real app, this would be API call)
    const validCredentials = [
      { username: 'admin', password: 'admin123' },
      { username: 'operator', password: 'operator123' },
      { username: 'demo', password: 'demo123' },
      { username: 'john', password: 'password' },
      { username: 'user', password: 'user123' },
      { username: 'manager', password: 'manager123' }
    ];

    console.log('Login attempt:', { username: `"${username}"`, password: `"${password}"` });
    console.log('Valid credentials:', validCredentials);

    setTimeout(() => {
      // Trim whitespace and convert to lowercase for comparison
      const trimmedUsername = username.trim().toLowerCase();
      const trimmedPassword = password.trim();
      
      const isValid = validCredentials.some(
        cred => cred.username.toLowerCase() === trimmedUsername && cred.password === trimmedPassword
      );

      console.log('After trimming:', { username: `"${trimmedUsername}"`, password: `"${trimmedPassword}"` });
      console.log('Credentials valid:', isValid);

      if (isValid) {
        console.log('Calling onLogin with:', username);
        onLogin(username);
      } else {
        console.log('Invalid credentials');
        setError('Invalid username or password');
      }
      setIsLoading(false);
    }, 1000); // Simulate API delay
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-900 to-gray-800 px-6 py-4">
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-2">
              <Mountain className="text-blue-400" size={28} />
              <Shield className="text-green-400" size={24} />
              <Zap className="text-yellow-400" size={20} />
            </div>
            <h1 className="text-white text-xl font-bold ml-3">AI Rockfall Monitor</h1>
          </div>
          <p className="text-gray-300 text-center mt-2 flex items-center justify-center">
            <Activity className="mr-2 text-blue-400" size={16} />
            Smart Mine Safety Platform
          </p>
        </div>

        {/* Login Form */}
        <div className="px-6 py-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Login to Dashboard</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your username"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
                isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                  Logging in...
                </div>
              ) : (
                'Login to Dashboard'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">🔑 Available Login Credentials:</h3>
            <div className="text-xs text-blue-700 space-y-1">
              <div><strong>Admin:</strong> admin / admin123 </div>
              <div><strong>Operator:</strong> operator / operator123 </div>
              <div><strong>Demo:</strong> demo / demo123 </div>
              <div><strong>User:</strong> john / password </div>
              <div><strong>User:</strong> user / user123 </div>
              <div><strong>Manager:</strong> manager / manager123 </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 text-center">
          <p className="text-sm text-gray-600">
            AI-Based Rockfall Risk Prediction System v1.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;