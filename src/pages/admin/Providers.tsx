import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users } from 'lucide-react';

const Providers = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Providers</h1>
          <p className="text-muted-foreground mt-2">Manage doctors and healthcare providers</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Provider List
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Provider management interface will be displayed here</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Providers;
