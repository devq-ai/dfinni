'use client';

import { useState } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function TestAuthPage() {
  const { isLoaded, userId, sessionId, getToken } = useAuth();
  const { user } = useUser();
  const [testResults, setTestResults] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const testClerkToken = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      setTestResults((prev: any) => ({ ...prev, clerkToken: token ? 'Retrieved' : 'No token' }));
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      
      // Test debug endpoint
      const debugResponse = await fetch(`${apiUrl}/api/v1/debug/auth-test`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const debugData = await debugResponse.json();
      setTestResults((prev: any) => ({ ...prev, debugEndpoint: debugData }));
      
      // Test authenticated endpoint
      const authResponse = await fetch(`${apiUrl}/api/v1/debug/auth-user`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const authData = await authResponse.json();
      setTestResults((prev: any) => ({ ...prev, authEndpoint: authData }));
      
      // Test patients endpoint
      const patientsResponse = await fetch(`${apiUrl}/api/v1/patients/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const patientsData = await patientsResponse.json();
      setTestResults((prev: any) => ({ ...prev, patientsEndpoint: patientsData }));
      
    } catch (error) {
      setTestResults((prev: any) => ({ ...prev, error: (error as Error).message }));
    }
    setLoading(false);
  };

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Authentication Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Clerk Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Loaded:</strong> {isLoaded ? 'Yes' : 'No'}</p>
            <p><strong>User ID:</strong> {userId || 'Not signed in'}</p>
            <p><strong>Session ID:</strong> {sessionId || 'No session'}</p>
            <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress || 'No email'}</p>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>API Test Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={testClerkToken} disabled={loading}>
            {loading ? 'Testing...' : 'Test Authentication'}
          </Button>
          
          {Object.keys(testResults).length > 0 && (
            <pre className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded overflow-auto">
              {JSON.stringify(testResults, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}