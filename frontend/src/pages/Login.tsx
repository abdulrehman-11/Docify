import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { login } from '@/lib/auth';
import { toast } from 'sonner';
import { Stethoscope, Lock, Mail } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const user = await login(email, password);
      if (user) {
        toast.success(`Welcome back, ${user.name}!`);
        navigate(user.role === 'admin' ? '/admin/dashboard' : '/staff/dashboard');
      } else {
        toast.error('Invalid email or password');
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-primary/5 to-secondary/5">
      <div className="w-full max-w-md">
        <div className="glass-card p-8 rounded-2xl animate-scale-in">
          <div className="text-center mb-8">
            <div className="inline-block p-3 rounded-2xl bg-gradient-to-br from-primary to-secondary mb-4">
              <Stethoscope className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Staff Login</h1>
            <p className="text-muted-foreground">Access your control panel</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="glass"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="glass"
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full gradient-primary text-white hover:opacity-90 transition-opacity"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          <div className="mt-6 p-4 glass rounded-xl">
            <p className="text-sm font-medium mb-2">Demo Credentials:</p>
            <div className="text-xs space-y-1 text-muted-foreground">
              <p>Admin: admin@clinic.com / Admin123</p>
              <p>Staff: staff@clinic.com / Staff123</p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <a href="/" className="text-sm text-primary hover:underline">
              ← Back to Home
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
