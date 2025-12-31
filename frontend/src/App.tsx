import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebaseConfig';
import './App.scss';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Interview from './components/Interview';

function App() {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [view, setView] = useState<'dashboard' | 'interview'>('dashboard');
  const [topic, setTopic] = useState<string>('');

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setSession(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLogin = (user: any) => {
    // Session set by onAuthStateChanged
    setView('dashboard');
  };

  const handleLogout = () => {
    auth.signOut();
    setView('dashboard');
    setTopic('');
  };

  const startInterview = (selectedTopic: string) => {
    setTopic(selectedTopic);
    setView('interview');
  };

  const endInterview = () => {
    setView('dashboard');
    setTopic('');
  };

  if (loading) return <div>Loading...</div>;

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      {view === 'dashboard' && (
        <Dashboard
          onStartInterview={startInterview}
          onLogout={handleLogout}
          userId={session.uid}
        />
      )}
      {view === 'interview' && (
        <Interview
          topic={topic}
          onEndInterview={endInterview}
          userId={session.uid}
        />
      )}
    </div>
  );
}

export default App;
