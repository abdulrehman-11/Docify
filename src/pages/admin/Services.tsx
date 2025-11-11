import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Briefcase } from 'lucide-react';

const Services = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Services</h1>
          <p className="text-muted-foreground mt-2">Manage clinic services and treatments</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Service List
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Service management interface will be displayed here</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Services;
