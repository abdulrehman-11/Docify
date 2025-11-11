import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2 } from 'lucide-react';

const Clinic = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Clinic Information</h1>
          <p className="text-muted-foreground mt-2">Manage clinic details and settings</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Clinic Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Clinic information editor will be displayed here</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Clinic;
