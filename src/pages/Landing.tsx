import { Navbar } from '@/components/layout/Navbar';
import { Button } from '@/components/ui/button';
import { 
  Phone, 
  Calendar, 
  MessageSquare, 
  Clock, 
  Mail, 
  MapPin,
  CheckCircle,
  Sparkles,
  Shield,
  Zap
} from 'lucide-react';

const Landing = () => {
  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <div className="animate-fade-in">
            <div className="inline-block mb-6">
              <span className="glass-card px-6 py-2 rounded-full text-sm font-medium text-primary">
                <Sparkles className="w-4 h-4 inline mr-2" />
                AI-Powered Healthcare
              </span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              Your AI-Powered
              <br />
              Clinic Receptionist
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Book appointments, get instant answers, and manage your healthcare needs 24/7 with our intelligent calling agent.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <a href="tel:+92444555777">
                <Button size="lg" className="gradient-primary text-white text-lg px-8 py-6 hover:scale-105 transition-transform">
                  <Phone className="w-5 h-5 mr-2" />
                  Call Now: +92-444-555-777
                </Button>
              </a>
              <Button size="lg" variant="outline" className="glass text-lg px-8 py-6 hover-lift">
                <Calendar className="w-5 h-5 mr-2" />
                View Doctors
              </Button>
            </div>
          </div>

          {/* Floating cards animation */}
          <div className="mt-20 grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { icon: Calendar, title: 'Book Appointments', delay: '0s' },
              { icon: MessageSquare, title: 'Get Instant Answers', delay: '0.2s' },
              { icon: Clock, title: 'Available 24/7', delay: '0.4s' },
            ].map((item, index) => (
              <div
                key={index}
                className="glass-card p-6 rounded-2xl hover-lift animate-float"
                style={{ animationDelay: item.delay }}
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-4 mx-auto">
                  <item.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-lg">{item.title}</h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4 bg-gradient-hero">
        <div className="container mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
            How It <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Works</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                step: '1',
                title: 'Call Our AI Agent',
                description: 'Simply call our number and speak naturally with our intelligent AI receptionist.',
                icon: Phone,
              },
              {
                step: '2',
                title: 'Get Instant Help',
                description: 'Book appointments, reschedule, or get answers to your questions instantly.',
                icon: Zap,
              },
              {
                step: '3',
                title: 'Receive Confirmation',
                description: 'Get immediate confirmation via SMS and email with all appointment details.',
                icon: CheckCircle,
              },
            ].map((item, index) => (
              <div key={index} className="glass-card p-8 rounded-2xl hover-lift text-center">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-6 mx-auto">
                  <item.icon className="w-8 h-8 text-white" />
                </div>
                <div className="text-4xl font-bold text-primary mb-4">{item.step}</div>
                <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                Welcome to{' '}
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  HealthCare Plus
                </span>
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                We're revolutionizing healthcare accessibility with our AI-powered calling agent system. 
                Our mission is to make healthcare booking effortless, available 24/7, and accessible to everyone.
              </p>
              <div className="space-y-4">
                {[
                  { icon: Shield, text: 'HIPAA Compliant & Secure' },
                  { icon: Clock, text: 'Available 24/7' },
                  { icon: Sparkles, text: 'Powered by Advanced AI' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <item.icon className="w-5 h-5 text-primary" />
                    </div>
                    <span className="font-medium">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-card p-8 rounded-2xl">
              <h3 className="text-2xl font-bold mb-6">Our Services</h3>
              <ul className="space-y-4">
                {[
                  'General Consultations',
                  'Specialist Appointments',
                  'Health Checkups',
                  'Vaccination Services',
                  'Laboratory Testing',
                  'Emergency Care',
                ].map((service, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-success" />
                    <span>{service}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4 bg-gradient-hero">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
            Get in <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">Touch</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="glass-card p-6 rounded-2xl text-center hover-lift">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-4 mx-auto">
                <Phone className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold mb-2">Phone</h3>
              <a href="tel:+92444555777" className="text-primary hover:underline">
                +92-444-555-777
              </a>
            </div>
            <div className="glass-card p-6 rounded-2xl text-center hover-lift">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-secondary to-accent flex items-center justify-center mb-4 mx-auto">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold mb-2">Email</h3>
              <a href="mailto:info@healthcareplus.com" className="text-primary hover:underline">
                info@healthcareplus.com
              </a>
            </div>
            <div className="glass-card p-6 rounded-2xl text-center hover-lift">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-primary flex items-center justify-center mb-4 mx-auto">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold mb-2">Address</h3>
              <p className="text-sm text-muted-foreground">
                123 Medical Center, Islamabad, Pakistan
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto text-center text-muted-foreground">
          <p>© 2025 HealthCare Plus Clinic. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
