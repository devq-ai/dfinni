export type ProviderRole = 'doctor' | 'nurse' | 'admin' | 'receptionist' | 'specialist';

export interface Provider {
  id: string;
  firstName: string;
  middleName?: string;
  lastName: string;
  email: string;
  phone: string;
  role: ProviderRole;
  specialization?: string;
  licenseNumber: string;
  department?: string;
  status: 'active' | 'inactive' | 'on_leave';
  hireDate: string;
  assignedPatients?: string[]; // Array of patient IDs
  createdAt: string;
  updatedAt: string;
}

export interface CreateProviderDto {
  firstName: string;
  middleName?: string;
  lastName: string;
  email: string;
  phone: string;
  role: ProviderRole;
  specialization?: string;
  licenseNumber: string;
  department?: string;
  status?: 'active' | 'inactive' | 'on_leave';
  hireDate: string;
}

export interface UpdateProviderDto extends Partial<CreateProviderDto> {
  assignedPatients?: string[];
}

export interface ProviderListResponse {
  providers: Provider[];
  total: number;
  page: number;
  pageSize: number;
}