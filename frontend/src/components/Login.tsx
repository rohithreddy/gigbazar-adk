import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebaseConfig';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Sparkles, Bot, Briefcase, Users, Zap, Shield, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

interface LoginProps {
    onLogin: (user: any) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            toast.success('Welcome back!');
            onLogin(userCredential.user);
        } catch (error: any) {
            console.error(error);
            toast.error('Invalid email or password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
            {/* Background decorations */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
            </div>

            <div className="w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center relative">
                {/* Left side - Branding and Features */}
                <div className="hidden lg:block space-y-8">
                    {/* Logo and Title */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="h-16 w-16 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 rounded-2xl flex items-center justify-center shadow-2xl">
                                <Sparkles className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                    GigBazar
                                </h1>
                                <div className="flex items-center gap-2">
                                    <Badge variant="secondary" className="text-xs">AI-Powered</Badge>
                                    <Badge variant="outline" className="text-xs">Interview Marketplace</Badge>
                                </div>
                            </div>
                        </div>
                        <p className="text-xl text-gray-600">
                            Transform your hiring process with AI-powered interview screening
                        </p>
                    </div>

                    {/* Features */}
                    <div className="space-y-4">
                        <div className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white shadow-sm">
                            <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Bot className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-900">AI Interviewers</h3>
                                <p className="text-sm text-gray-600">Dedicated AI agents for each position with custom instructions</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white shadow-sm">
                            <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Briefcase className="h-5 w-5 text-purple-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-900">Smart Job Matching</h3>
                                <p className="text-sm text-gray-600">Tailored interviews based on skills and experience level</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white shadow-sm">
                            <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Zap className="h-5 w-5 text-green-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-900">Instant Results</h3>
                                <p className="text-sm text-gray-600">Complete transcripts and insights delivered immediately</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white shadow-sm">
                            <div className="h-10 w-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                <Users className="h-5 w-5 text-orange-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-900">Scale Your Hiring</h3>
                                <p className="text-sm text-gray-600">Screen unlimited candidates without scheduling conflicts</p>
                            </div>
                        </div>
                    </div>

                    {/* Trust indicators */}
                    <div className="flex items-center gap-6 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                            <Shield className="h-4 w-4 text-green-600" />
                            <span>Secure & Private</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            <span>GDPR Compliant</span>
                        </div>
                    </div>
                </div>

                {/* Right side - Login Form */}
                <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
                    <CardHeader className="space-y-1 pb-6">
                        <div className="flex items-center gap-3 lg:hidden mb-4">
                            <div className="h-12 w-12 bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
                                <Sparkles className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                    GigBazar
                                </h1>
                                <Badge variant="secondary" className="text-xs">AI Interview Marketplace</Badge>
                            </div>
                        </div>
                        <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
                        <CardDescription>
                            Sign in to your HR dashboard to manage job postings and review interviews
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="your.email@company.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="h-11"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="h-11"
                                />
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-11 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg"
                                disabled={loading}
                            >
                                {loading ? (
                                    <div className="flex items-center gap-2">
                                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                        Signing in...
                                    </div>
                                ) : (
                                    'Sign in'
                                )}
                            </Button>
                        </form>

                        <div className="mt-6 text-center text-sm text-gray-600">
                            <p>Demo credentials for testing:</p>
                            <p className="text-xs text-gray-500 mt-1">Email: crash@myhoma.in | Password: crash1234</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Login;
