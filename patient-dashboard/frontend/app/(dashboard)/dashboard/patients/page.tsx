// Last Updated: 2025-08-09T20:12:00-06:00
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { usePatientsApi } from '@/lib/api/patients-client';
import { Patient, CreatePatientDto, UpdatePatientDto } from '@/types/patient';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, UserPlus, Edit, Trash2, Eye } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { PatientForm } from "@/components/patient-form";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function PatientsPage() {
  const searchParams = useSearchParams();
  const filter = searchParams.get('filter');
  const { toast } = useToast();
  const patientsApi = usePatientsApi();
  
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [patientToDelete, setPatientToDelete] = useState<Patient | null>(null);

  useEffect(() => {
    fetchPatients();
  }, [filter]);

  const fetchPatients = async () => {
    try {
      const response = await patientsApi.getPatients();
      let filteredPatients = response.patients;
      
      // Apply filters based on query parameter
      if (filter === 'high-risk') {
        // High risk patients are those with risk level 'High' AND not churned
        filteredPatients = filteredPatients.filter(p => 
          p.riskLevel === 'High' && p.status !== 'churned'
        );
      } else if (filter === 'active') {
        filteredPatients = filteredPatients.filter(p => p.status === 'active');
      }
      
      setPatients(filteredPatients);
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      toast({
        title: "Error",
        description: "Failed to fetch patients",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePatient = async (data: CreatePatientDto) => {
    try {
      await patientsApi.createPatient(data);
      toast({
        title: "Success",
        description: "Patient created successfully",
      });
      setIsFormOpen(false);
      fetchPatients();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create patient",
        variant: "destructive",
      });
    }
  };

  const handleUpdatePatient = async (data: CreatePatientDto) => {
    if (!selectedPatient) return;
    
    try {
      const updateData: UpdatePatientDto = {
        ...data,
        status: data.status,
      };
      await patientsApi.updatePatient(selectedPatient.id, updateData);
      toast({
        title: "Success",
        description: "Patient updated successfully",
      });
      setIsFormOpen(false);
      setSelectedPatient(null);
      fetchPatients();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update patient",
        variant: "destructive",
      });
    }
  };

  const handleDeletePatient = async () => {
    if (!patientToDelete) return;
    
    try {
      await patientsApi.deletePatient(patientToDelete.id);
      toast({
        title: "Success",
        description: "Patient deleted successfully",
      });
      setIsDeleteOpen(false);
      setPatientToDelete(null);
      fetchPatients();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete patient",
        variant: "destructive",
      });
    }
  };

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = 
      `${patient.firstName} ${patient.middleName || ''} ${patient.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (patient.email?.toLowerCase().includes(searchTerm.toLowerCase()) || false) ||
      patient.mrn.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || patient.status.toLowerCase() === statusFilter.toLowerCase();
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-cyber-matrix-green text-cyber-void-black';
      case 'inquiry':
        return 'bg-cyber-electric-cyan text-cyber-void-black';
      case 'onboarding':
        return 'bg-yellow-500 text-cyber-void-black';
      case 'churned':
        return 'bg-cyber-neon-pink text-cyber-white';
      case 'urgent':
        return 'bg-red-600 text-white';
      default:
        return 'bg-cyber-gray text-cyber-white';
    }
  };

  const formatAddress = (address: Patient['address']) => {
    return `${address.street}, ${address.city}, ${address.state} ${address.zip}`;
  };

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Patients
            {filter === 'high-risk' && (
              <span className="ml-2 text-lg font-normal text-orange-500">(High Risk)</span>
            )}
            {filter === 'active' && (
              <span className="ml-2 text-lg font-normal text-green-500">(Active)</span>
            )}
          </h1>
          <p className="text-muted-foreground">Manage and view patient information</p>
        </div>
        <Button 
          className="bg-cyber-electric-cyan text-cyber-void-black hover:bg-cyber-matrix-green"
          onClick={() => {
            setSelectedPatient(null);
            setIsFormOpen(true);
          }}
        >
          <UserPlus className="mr-2 h-4 w-4" />
          Add Patient
        </Button>
      </div>

      <Card className="bg-card border-2 border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
        <CardHeader>
          <CardTitle>Patient List</CardTitle>
          <CardDescription>A comprehensive list of all patients</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex items-center space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, email, or MRN..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px] dark:bg-[#0a0a0a] dark:border-[#3e3e3e]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="inquiry">Inquiry</SelectItem>
                <SelectItem value="onboarding">Onboarding</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="churned">Churned</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {loading ? (
            <div className="text-center py-8">Loading patients...</div>
          ) : filteredPatients.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No patients found. Click "Add Patient" to create a new patient record.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="dark:border-[#3e3e3e]">
                    <TableHead>Name</TableHead>
                    <TableHead>Date of Birth</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Address</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPatients.map((patient) => (
                    <TableRow key={patient.id} className="dark:border-[#3e3e3e]">
                      <TableCell className="font-medium">
                        {patient.firstName} {patient.middleName ? `${patient.middleName} ` : ''}{patient.lastName}
                      </TableCell>
                      <TableCell>{new Date(patient.dateOfBirth).toLocaleDateString()}</TableCell>
                      <TableCell>{calculateAge(patient.dateOfBirth)} years</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(patient.status)}>
                          {patient.status.charAt(0).toUpperCase() + patient.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {patient.riskLevel && (
                          <Badge 
                            variant={
                              patient.riskLevel === 'High' ? 'destructive' : 
                              patient.riskLevel === 'Medium' ? 'default' : 
                              'secondary'
                            }
                          >
                            {patient.riskLevel}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {formatAddress(patient.address)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              setSelectedPatient(patient);
                              setIsViewOpen(true);
                            }}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              setSelectedPatient(patient);
                              setIsFormOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              setPatientToDelete(patient);
                              setIsDeleteOpen(true);
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Patient Dialog */}
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedPatient ? 'Edit' : 'Create'} Patient</DialogTitle>
            <DialogDescription>
              {selectedPatient ? 'Update patient information' : 'Enter patient information to create a new record'}
            </DialogDescription>
          </DialogHeader>
          <PatientForm
            patient={selectedPatient || undefined}
            onSubmit={selectedPatient ? handleUpdatePatient : handleCreatePatient}
            onCancel={() => {
              setIsFormOpen(false);
              setSelectedPatient(null);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* View Patient Dialog */}
      <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Patient Details</DialogTitle>
          </DialogHeader>
          {selectedPatient && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Full Name</p>
                  <p className="text-lg">
                    {selectedPatient.firstName} {selectedPatient.middleName || ''} {selectedPatient.lastName}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">MRN</p>
                  <p className="text-lg">{selectedPatient.mrn}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Date of Birth</p>
                  <p className="text-lg">{new Date(selectedPatient.dateOfBirth).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Age</p>
                  <p className="text-lg">{calculateAge(selectedPatient.dateOfBirth)} years</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Status</p>
                  <Badge className={getStatusColor(selectedPatient.status)}>
                    {selectedPatient.status.charAt(0).toUpperCase() + selectedPatient.status.slice(1)}
                  </Badge>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Address</p>
                <p className="text-lg">{formatAddress(selectedPatient.address)}</p>
              </div>
              {selectedPatient.email && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Email</p>
                  <p className="text-lg">{selectedPatient.email}</p>
                </div>
              )}
              {selectedPatient.phone && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Phone</p>
                  <p className="text-lg">{selectedPatient.phone}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the patient record for{' '}
              {patientToDelete && `${patientToDelete.firstName} ${patientToDelete.lastName}`}.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setPatientToDelete(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeletePatient}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}