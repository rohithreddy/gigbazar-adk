import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebaseConfig';
import { Toaster } from 'sonner';
import './App.scss';
import Login from './components/Login';
import { HRDashboard } from './components/hr/HRDashboard';
import { PublicInterview } from './components/PublicInterview';
import { InterviewDetail } from './components/hr/InterviewDetail';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Wrapper component to access route params
function InterviewDetailWrapper({ apiUrl }: { apiUrl: string }) {
  const { interviewId } = useParams<{ interviewId: string }>();
  return <InterviewDetail apiUrl={apiUrl} interviewId={interviewId || ''} />;
}

function App() {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setSession(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLogin = (user: any) => {
    // Session set by onAuthStateChanged
  };

  const handleLogout = () => {
    auth.signOut();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        {/* Public interview route - no auth required */}
        <Route path="/interview/:shareToken" element={<PublicInterview apiUrl={API_URL} />} />

        {/* Protected HR routes */}
        <Route
          path="/"
          element={
            !session ? (
              <Login onLogin={handleLogin} />
            ) : (
              <Navigate to="/hr" replace />
            )
          }
        />
        <Route
          path="/hr"
          element={
            session ? (
              <HRDashboard
                userId={session.uid}
                userEmail={session.email || undefined}
                userName={session.displayName || undefined}
                onLogout={handleLogout}
                apiUrl={API_URL}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route
          path="/interview-detail/:interviewId"
          element={
            session ? (
              <InterviewDetailWrapper apiUrl={API_URL} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
