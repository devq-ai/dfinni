import { UserProfile } from '@clerk/nextjs';

export default function SettingsPage() {
  return (
    <div className='flex w-full flex-col p-4'>
      <UserProfile />
    </div>
  );
}