import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClipboardList } from 'lucide-react';

const Audit = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Audit Log</h1>
          <p className="text-muted-foreground mt-2">View all system activities and changes</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="w-5 h-5" />
              Activity Log
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Audit log table will be displayed here</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Audit;
