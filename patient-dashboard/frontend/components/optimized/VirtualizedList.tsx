'use client';

import React, { useCallback, memo } from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';
import { Patient } from '@/types/patient';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface VirtualizedPatientListProps {
  patients: Patient[];
  onPatientClick?: (patient: Patient) => void;
}

// Memoized row component
const PatientRow = memo(({ 
  index, 
  style, 
  data 
}: { 
  index: number; 
  style: React.CSSProperties; 
  data: { patients: Patient[]; onPatientClick?: (patient: Patient) => void } 
}) => {
  const patient = data.patients[index];
  const handleClick = useCallback(() => {
    data.onPatientClick?.(patient);
  }, [data.onPatientClick, patient]);

  return (
    <div style={style} className="px-4 py-2">
      <Card 
        className="cursor-pointer hover:shadow-md transition-shadow"
        onClick={handleClick}
      >
        <CardContent className="p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-lg">
                {patient.firstName} {patient.lastName}
              </h3>
              <p className="text-sm text-muted-foreground">
                MRN: {patient.medicalRecordNumber}
              </p>
              <p className="text-sm text-muted-foreground">
                DOB: {new Date(patient.dateOfBirth).toLocaleDateString()}
              </p>
            </div>
            <div className="flex flex-col gap-2">
              <Badge 
                variant={patient.status === 'Active' ? 'default' : 'secondary'}
              >
                {patient.status}
              </Badge>
              <Badge 
                variant={
                  patient.riskLevel === 'High' ? 'destructive' : 
                  patient.riskLevel === 'Medium' ? 'warning' : 
                  'secondary'
                }
              >
                {patient.riskLevel} Risk
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
});

PatientRow.displayName = 'PatientRow';

export const VirtualizedPatientList: React.FC<VirtualizedPatientListProps> = memo(({ 
  patients, 
  onPatientClick 
}) => {
  // Memoize item data to prevent unnecessary re-renders
  const itemData = React.useMemo(
    () => ({ patients, onPatientClick }),
    [patients, onPatientClick]
  );

  return (
    <div className="h-[600px] w-full">
      <AutoSizer>
        {({ height, width }) => (
          <List
            height={height}
            itemCount={patients.length}
            itemSize={120} // Height of each row
            width={width}
            itemData={itemData}
            overscanCount={5} // Render 5 items outside of visible area
          >
            {PatientRow}
          </List>
        )}
      </AutoSizer>
    </div>
  );
});

VirtualizedPatientList.displayName = 'VirtualizedPatientList';

// Export a lazy-loaded version
export { VirtualizedPatientList as default };