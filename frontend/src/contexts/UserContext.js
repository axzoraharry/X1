import React, { createContext, useContext, useState, useEffect } from 'react';
import { userService } from '../services/userService';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // For demo purposes, we'll use the demo user
    // In production, this would check for authentication tokens
    const initializeUser = async () => {
      try {
        setLoading(true);
        const demoUser = await userService.getDemoUser();
        setUser(demoUser);
      } catch (err) {
        setError(err.message);
        console.error('Failed to initialize user:', err);
      } finally {
        setLoading(false);
      }
    };

    initializeUser();
  }, []);

  const updateUser = async (userData) => {
    try {
      if (user) {
        const updatedUser = await userService.updateUser(user.id, userData);
        setUser(updatedUser);
        return updatedUser;
      }
    } catch (err) {
      console.error('Failed to update user:', err);
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    // In production, clear authentication tokens
  };

  const value = {
    user,
    loading,
    error,
    updateUser,
    logout,
    isAuthenticated: !!user
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};