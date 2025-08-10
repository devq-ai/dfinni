// Last Updated: 2025-08-09T20:12:00-06:00
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { providersApi } from '@/lib/api/providers';
import { Provider, CreateProviderDto, ProviderRole } from '@/types/provider';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, UserPlus } from "lucide-react";

export default function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newProvider, setNewProvider] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    specialization: '',
    licenseNumber: '',
    department: '',
    status: 'active',
    hireDate: new Date().toISOString().split('T')[0] // Default to today
  });

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const response = await providersApi.getProviders();
        setProviders(response.providers);
      } catch (error) {
        console.error('Failed to fetch providers:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProviders();
  }, []);

  const handleAddProvider = async () => {
    try {
      const providerData: CreateProviderDto = {
        firstName: newProvider.firstName,
        lastName: newProvider.lastName,
        email: newProvider.email,
        phone: newProvider.phone,
        role: newProvider.role as ProviderRole,
        specialization: newProvider.specialization,
        licenseNumber: newProvider.licenseNumber,
        department: newProvider.department,
        status: newProvider.status as 'active' | 'inactive' | 'on_leave',
        hireDate: newProvider.hireDate
      };
      const provider = await providersApi.createProvider(providerData);
      setProviders([...providers, provider]);
      setNewProvider({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        role: '',
        specialization: '',
        licenseNumber: '',
        department: '',
        status: 'active',
        hireDate: new Date().toISOString().split('T')[0]
      });
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Failed to create provider:', error);
    }
  };

  const filteredProviders = providers.filter(provider => {
    const fullName = `${provider.firstName} ${provider.lastName}`.toLowerCase();
    return fullName.includes(searchTerm.toLowerCase()) ||
      provider.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      provider.licenseNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (provider.specialization?.toLowerCase().includes(searchTerm.toLowerCase()) || false);
  });

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'doctor':
        return 'bg-cyber-electric-cyan text-cyber-void-black';
      case 'nurse':
        return 'bg-cyber-matrix-green text-cyber-void-black';
      case 'admin':
        return 'bg-cyber-neon-pink text-cyber-white';
      case 'specialist':
        return 'bg-blue-500 text-white';
      default:
        return 'bg-cyber-gray text-cyber-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-cyber-matrix-green text-cyber-void-black';
      case 'inactive':
        return 'bg-cyber-gray text-cyber-white';
      case 'on_leave':
        return 'bg-orange-500 text-white';
      default:
        return 'bg-cyber-electric-cyan text-cyber-void-black';
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Providers</h1>
          <p className="text-muted-foreground">Manage healthcare providers and staff</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-cyber-electric-cyan text-cyber-void-black hover:bg-cyber-matrix-green">
              <UserPlus className="mr-2 h-4 w-4" />
              Add Provider
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px] dark:bg-[#141414] dark:border-[#3e3e3e]">
            <DialogHeader>
              <DialogTitle>Add New Provider</DialogTitle>
              <DialogDescription>
                Add a new healthcare provider to the system.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={newProvider.firstName}
                    onChange={(e) => setNewProvider({...newProvider, firstName: e.target.value})}
                    className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={newProvider.lastName}
                    onChange={(e) => setNewProvider({...newProvider, lastName: e.target.value})}
                    className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={newProvider.email}
                  onChange={(e) => setNewProvider({...newProvider, email: e.target.value})}
                  className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={newProvider.phone}
                  onChange={(e) => setNewProvider({...newProvider, phone: e.target.value})}
                  className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="role">Role</Label>
                  <Select value={newProvider.role} onValueChange={(value) => setNewProvider({...newProvider, role: value})}>
                    <SelectTrigger className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]">
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent className="dark:bg-[#141414] dark:border-[#3e3e3e]">
                      <SelectItem value="doctor">Doctor</SelectItem>
                      <SelectItem value="nurse">Nurse</SelectItem>
                      <SelectItem value="specialist">Specialist</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={newProvider.department}
                    onChange={(e) => setNewProvider({...newProvider, department: e.target.value})}
                    className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="specialization">Specialization</Label>
                <Input
                  id="specialization"
                  value={newProvider.specialization}
                  onChange={(e) => setNewProvider({...newProvider, specialization: e.target.value})}
                  className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="licenseNumber">License Number</Label>
                <Input
                  id="licenseNumber"
                  value={newProvider.licenseNumber}
                  onChange={(e) => setNewProvider({...newProvider, licenseNumber: e.target.value})}
                  className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="hireDate">Hire Date</Label>
                <Input
                  id="hireDate"
                  type="date"
                  value={newProvider.hireDate}
                  onChange={(e) => setNewProvider({...newProvider, hireDate: e.target.value})}
                  className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)} className="dark:border-[#3e3e3e]">
                Cancel
              </Button>
              <Button 
                onClick={handleAddProvider}
                className="bg-cyber-electric-cyan text-cyber-void-black hover:bg-cyber-matrix-green"
                disabled={!newProvider.firstName || !newProvider.lastName || !newProvider.email || !newProvider.role}
              >
                Add Provider
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-card border-2 border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
        <CardHeader>
          <CardTitle>Provider List</CardTitle>
          <CardDescription>All healthcare providers and staff members</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex items-center space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search providers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">Loading providers...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="dark:border-[#3e3e3e]">
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>License #</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Patients</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProviders.map((provider) => (
                  <TableRow key={provider.id} className="dark:border-[#3e3e3e]">
                    <TableCell className="font-medium">
                      {provider.firstName} {provider.middleName ? `${provider.middleName} ` : ''}{provider.lastName}
                      {provider.specialization && (
                        <div className="text-xs text-muted-foreground">{provider.specialization}</div>
                      )}
                    </TableCell>
                    <TableCell>{provider.email}</TableCell>
                    <TableCell>
                      <Badge className={getRoleColor(provider.role)}>
                        {provider.role}
                      </Badge>
                    </TableCell>
                    <TableCell>{provider.department || 'N/A'}</TableCell>
                    <TableCell>{provider.licenseNumber}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(provider.status)}>
                        {provider.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>{provider.assignedPatients?.length || 0}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" className="dark:border-[#3e3e3e]">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}