'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { providersApi } from '@/lib/api/providers';
import { Provider } from '@/types/provider';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, UserPlus } from "lucide-react";

export default function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

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
        <Button className="bg-cyber-electric-cyan text-cyber-void-black hover:bg-cyber-matrix-green">
          <UserPlus className="mr-2 h-4 w-4" />
          Add Provider
        </Button>
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