import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-cyber-void-black">
      <div className="w-full max-w-md">
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "bg-cyber-carbon-black border border-cyber-gray shadow-xl",
              headerTitle: "text-cyber-white",
              headerSubtitle: "text-cyber-white/70",
              socialButtonsIconButton: "border-cyber-gray hover:border-cyber-electric-cyan",
              formButtonPrimary: "bg-cyber-electric-cyan hover:bg-cyber-matrix-green text-cyber-void-black",
              formFieldInput: "bg-cyber-gray border-cyber-gray text-cyber-white",
              formFieldLabel: "text-cyber-white",
              footerActionLink: "text-cyber-electric-cyan hover:text-cyber-matrix-green",
            }
          }}
          redirectUrl="/dashboard"
          signInUrl="/login"
        />
      </div>
    </div>
  );
}