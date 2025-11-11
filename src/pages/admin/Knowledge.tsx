import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen } from 'lucide-react';

const Knowledge = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Knowledge Base</h1>
          <p className="text-muted-foreground mt-2">Manage AI responses and FAQs</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              AI Responses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Knowledge base editor will be displayed here</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Knowledge;
