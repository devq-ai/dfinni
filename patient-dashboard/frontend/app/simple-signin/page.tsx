'use client';

import { SignIn } from '@clerk/nextjs';

export default function SimpleSignIn() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      backgroundColor: '#ffffff'
    }}>
      <SignIn 
        path="/simple-signin"
        routing="path"
        signUpUrl="/sign-up"
        afterSignInUrl="/dashboard"
      />
    </div>
  );
}