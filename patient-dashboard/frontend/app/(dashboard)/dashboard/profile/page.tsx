'use client';

import { useUser } from '@clerk/nextjs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { User, Mail, Phone, MapPin, Calendar, Shield, Settings } from "lucide-react";

export default function ProfilePage() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!user) {
    return <div className="flex items-center justify-center h-screen">Please sign in to view your profile.</div>;
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
          <p className="text-muted-foreground">Manage your account settings and preferences</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="bg-card border-2 border-border dark:bg-[#141414] dark:border-[#3e3e3e] md:col-span-1">
          <CardHeader className="text-center">
            <Avatar className="h-32 w-32 mx-auto mb-4 border-4 border-cyber-electric-cyan">
              <AvatarImage src={user.imageUrl} alt={user.fullName || ''} />
              <AvatarFallback className="text-2xl bg-cyber-gray">
                {getInitials(user.fullName || user.emailAddresses[0].emailAddress)}
              </AvatarFallback>
            </Avatar>
            <CardTitle>{user.fullName || 'User'}</CardTitle>
            <CardDescription>{user.emailAddresses[0].emailAddress}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-center text-muted-foreground">
                <Calendar className="h-4 w-4 mr-2" />
                Joined {new Date(user.createdAt!).toLocaleDateString()}
              </div>
              <div className="flex items-center text-muted-foreground">
                <Shield className="h-4 w-4 mr-2" />
                {(user.publicMetadata as any)?.role || 'Healthcare Provider'}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-2 border-border dark:bg-[#141414] dark:border-[#3e3e3e] md:col-span-2">
          <Tabs defaultValue="personal" className="h-full">
            <CardHeader>
              <TabsList className="grid w-full grid-cols-3 dark:bg-[#0a0a0a]">
                <TabsTrigger value="personal">Personal Info</TabsTrigger>
                <TabsTrigger value="security">Security</TabsTrigger>
                <TabsTrigger value="preferences">Preferences</TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent>
              <TabsContent value="personal" className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input
                      id="firstName"
                      value={user.firstName || ''}
                      disabled
                      className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input
                      id="lastName"
                      value={user.lastName || ''}
                      disabled
                      className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={user.emailAddresses[0].emailAddress}
                      disabled
                      className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="Add phone number"
                      className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <textarea
                    id="bio"
                    placeholder="Tell us about yourself..."
                    className="w-full min-h-[100px] rounded-md border border-input bg-transparent px-3 py-2 text-sm dark:bg-[#0a0a0a] dark:border-[#3e3e3e]"
                  />
                </div>
                <Button className="bg-cyber-electric-cyan text-cyber-void-black hover:bg-cyber-matrix-green">
                  Save Changes
                </Button>
              </TabsContent>

              <TabsContent value="security" className="space-y-4">
                <Card className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]">
                  <CardHeader>
                    <CardTitle className="text-lg">Two-Factor Authentication</CardTitle>
                    <CardDescription>Add an extra layer of security to your account</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="outline" className="dark:border-[#3e3e3e]">
                      Enable 2FA
                    </Button>
                  </CardContent>
                </Card>
                <Card className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]">
                  <CardHeader>
                    <CardTitle className="text-lg">Active Sessions</CardTitle>
                    <CardDescription>Manage your active sessions across devices</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="outline" className="dark:border-[#3e3e3e]">
                      View Sessions
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="preferences" className="space-y-4">
                <Card className="dark:bg-[#0a0a0a] dark:border-[#3e3e3e]">
                  <CardHeader>
                    <CardTitle className="text-lg">Notification Settings</CardTitle>
                    <CardDescription>Configure how you receive notifications</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Email Notifications</p>
                        <p className="text-sm text-muted-foreground">Receive alerts via email</p>
                      </div>
                      <Button variant="outline" size="sm" className="dark:border-[#3e3e3e]">
                        Configure
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Push Notifications</p>
                        <p className="text-sm text-muted-foreground">Get instant alerts on your device</p>
                      </div>
                      <Button variant="outline" size="sm" className="dark:border-[#3e3e3e]">
                        Configure
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}