import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Phone, Stethoscope } from 'lucide-react';

export const Navbar = () => {
  return (
    <nav className="fixed top-0 w-full z-50 glass-card border-b border-white/20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-secondary group-hover:scale-110 transition-transform">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              HealthCare Plus
            </span>
          </Link>

          <div className="flex items-center gap-6">
            <a href="#about" className="text-foreground hover:text-primary transition-colors">
              About
            </a>
            <a href="#how-it-works" className="text-foreground hover:text-primary transition-colors">
              How It Works
            </a>
            <a href="#contact" className="text-foreground hover:text-primary transition-colors">
              Contact
            </a>
            <Link to="/login">
              <Button 
                variant="outline" 
                className="glass hover:bg-primary/10 hover:text-primary hover:border-primary/30 transition-all"
              >
                Staff Login
              </Button>
            </Link>
            <a href="tel:+92444555777">
              <Button className="gradient-primary text-white hover:opacity-90 transition-opacity">
                <Phone className="w-4 h-4 mr-2" />
                Call Now
              </Button>
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};
