import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BookOpen, Plus, Edit, Trash2, MessageSquare, Search } from 'lucide-react';
import { KnowledgeBaseItem } from '@/lib/mockData';
import { getKnowledgeBase, saveKnowledgeBaseItem, deleteKnowledgeBaseItem } from '@/lib/storage';
import { toast } from 'sonner';

const CATEGORIES = ['Appointments', 'Services', 'Clinic Hours', 'Insurance', 'Parking', 'General', 'Policies'];

const Knowledge = () => {
  const [items, setItems] = useState<KnowledgeBaseItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<KnowledgeBaseItem[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<KnowledgeBaseItem | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  const [formData, setFormData] = useState({
    category: '',
    question: '',
    answer: '',
  });

  useEffect(() => {
    loadItems();
  }, []);

  useEffect(() => {
    filterItems();
  }, [items, searchQuery, selectedCategory]);

  const loadItems = () => {
    setItems(getKnowledgeBase());
  };

  const filterItems = () => {
    let filtered = items;

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.answer.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredItems(filtered);
  };

  const handleAddItem = () => {
    setSelectedItem(null);
    setFormData({ category: '', question: '', answer: '' });
    setDialogOpen(true);
  };

  const handleEditItem = (item: KnowledgeBaseItem) => {
    setSelectedItem(item);
    setFormData({
      category: item.category,
      question: item.question,
      answer: item.answer,
    });
    setDialogOpen(true);
  };

  const handleDeleteItem = (id: string) => {
    setItemToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (itemToDelete) {
      deleteKnowledgeBaseItem(itemToDelete);
      loadItems();
      toast.success('Knowledge base item deleted successfully');
    }
    setDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  const handleSave = () => {
    if (!formData.category || !formData.question || !formData.answer) {
      toast.error('Please fill in all fields');
      return;
    }

    const itemData: KnowledgeBaseItem = {
      id: selectedItem?.id || Date.now().toString(),
      category: formData.category,
      question: formData.question,
      answer: formData.answer,
      lastUpdated: new Date().toISOString(),
    };

    saveKnowledgeBaseItem(itemData);
    loadItems();
    toast.success(selectedItem ? 'Knowledge base updated successfully' : 'Knowledge base item added successfully');
    setDialogOpen(false);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Appointments': 'bg-blue-100 text-blue-700',
      'Services': 'bg-green-100 text-green-700',
      'Clinic Hours': 'bg-purple-100 text-purple-700',
      'Insurance': 'bg-yellow-100 text-yellow-700',
      'Parking': 'bg-pink-100 text-pink-700',
      'General': 'bg-gray-100 text-gray-700',
      'Policies': 'bg-orange-100 text-orange-700',
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Base</h1>
            <p className="text-muted-foreground mt-2">Manage AI responses for common questions</p>
          </div>
          <Button onClick={handleAddItem} className="bg-primary hover-lift">
            <Plus className="w-4 h-4 mr-2" />
            Add Q&A
          </Button>
        </div>

        {/* Filters */}
        <Card className="glass-card">
          <CardContent className="pt-6">
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-[250px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search questions and answers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Knowledge Base Items */}
        <div className="space-y-4">
          {filteredItems.map((item) => (
            <Card key={item.id} className="glass-card hover-lift">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <Badge className={getCategoryColor(item.category)}>
                    {item.category}
                  </Badge>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditItem(item)}
                      className="hover-lift"
                    >
                      <Edit className="w-3 h-3 mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteItem(item.id)}
                      className="hover-lift text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Delete
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex items-start gap-2 mb-1">
                      <MessageSquare className="w-4 h-4 text-primary mt-1" />
                      <p className="font-semibold text-lg">{item.question}</p>
                    </div>
                  </div>

                  <div className="pl-6">
                    <p className="text-muted-foreground whitespace-pre-wrap">{item.answer}</p>
                  </div>

                  <div className="pl-6 pt-2 border-t">
                    <p className="text-xs text-muted-foreground">
                      Last updated: {new Date(item.lastUpdated).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {filteredItems.length === 0 && (
            <Card className="glass-card">
              <CardContent className="text-center py-12">
                <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                <p className="text-muted-foreground mb-4">
                  {searchQuery || selectedCategory !== 'all'
                    ? 'No items found matching your filters'
                    : 'No knowledge base items yet'}
                </p>
                {!searchQuery && selectedCategory === 'all' && (
                  <Button onClick={handleAddItem} variant="outline" className="hover-lift">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Your First Q&A
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="glass-card sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>
                {selectedItem ? 'Edit Knowledge Base Item' : 'Add New Knowledge Base Item'}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((cat) => (
                      <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="question">Question *</Label>
                <Input
                  id="question"
                  value={formData.question}
                  onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                  placeholder="How do I book an appointment?"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="answer">AI Response *</Label>
                <Textarea
                  id="answer"
                  value={formData.answer}
                  onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                  placeholder="You can book an appointment by calling our AI receptionist at +92-444-555-777..."
                  rows={6}
                />
                <p className="text-xs text-muted-foreground">
                  This is the exact answer the AI will give when asked this question
                </p>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} className="bg-primary">
                {selectedItem ? 'Update' : 'Add'} Item
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent className="glass-card">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Knowledge Base Item?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this Q&A item. The AI will no longer have this information. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={confirmDelete} className="bg-destructive">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </DashboardLayout>
  );
};

export default Knowledge;
