import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { profileAPI } from '@/lib/api'
import { Camera, Save, Lock, Bell, User } from 'lucide-react'
import toast from 'react-hot-toast'

interface NotificationPreferences {
  email_notifications: boolean
  sms_notifications: boolean
  push_notifications: boolean
}

export default function Profile() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'notifications'>('profile')
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    language: 'en',
    timezone: 'UTC',
    date_format: 'DD/MM/YYYY',
  })

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  // Notification preferences state
  const [notificationPrefs, setNotificationPrefs] = useState<NotificationPreferences>({
    email_notifications: true,
    sms_notifications: false,
    push_notifications: true,
  })

  // Fetch profile data
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: profileAPI.get,
  })

  // Update form when profile data loads
  useEffect(() => {
    if (profile) {
      setProfileForm({
        full_name: profile.full_name,
        email: profile.email,
        phone: profile.phone,
        language: profile.language,
        timezone: profile.timezone,
        date_format: profile.date_format,
      })
    }
  }, [profile])

  // Fetch notification preferences
  const { data: notifications } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: profileAPI.getNotificationPreferences,
  })

  // Update notification prefs when data loads
  useEffect(() => {
    if (notifications) {
      setNotificationPrefs(notifications)
    }
  }, [notifications])

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: profileAPI.update,
    onSuccess: () => {
      toast.success('Profile updated successfully')
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => {
      toast.error('Failed to update profile')
    },
  })

  // Upload photo mutation
  const uploadPhotoMutation = useMutation({
    mutationFn: profileAPI.uploadPhoto,
    onSuccess: () => {
      toast.success('Profile photo updated successfully')
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setPhotoFile(null)
      setPhotoPreview(null)
    },
    onError: () => {
      toast.error('Failed to upload photo')
    },
  })

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: profileAPI.changePassword,
    onSuccess: () => {
      toast.success('Password changed successfully')
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    },
    onError: () => {
      toast.error('Failed to change password')
    },
  })

  // Update notification preferences mutation
  const updateNotificationsMutation = useMutation({
    mutationFn: profileAPI.updateNotificationPreferences,
    onSuccess: () => {
      toast.success('Notification preferences updated')
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] })
    },
    onError: () => {
      toast.error('Failed to update preferences')
    },
  })

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file')
        return
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image size must be less than 5MB')
        return
      }
      setPhotoFile(file)
      setPhotoPreview(URL.createObjectURL(file))
    }
  }

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateProfileMutation.mutate(profileForm)
  }

  const handlePhotoUpload = () => {
    if (photoFile) {
      uploadPhotoMutation.mutate(photoFile)
    }
  }

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Passwords do not match')
      return
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    changePasswordMutation.mutate({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    })
  }

  const handleNotificationsSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateNotificationsMutation.mutate(notificationPrefs)
  }

  const getPasswordStrength = (password: string) => {
    if (password.length === 0) return { strength: 0, label: '' }
    if (password.length < 6) return { strength: 25, label: 'Weak', color: 'bg-red-500' }
    if (password.length < 10) return { strength: 50, label: 'Fair', color: 'bg-yellow-500' }
    if (password.length < 14) return { strength: 75, label: 'Good', color: 'bg-blue-500' }
    return { strength: 100, label: 'Strong', color: 'bg-green-500' }
  }

  const passwordStrength = getPasswordStrength(passwordForm.new_password)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const tabs = [
    { id: 'profile' as const, label: 'Profile', icon: User },
    { id: 'password' as const, label: 'Security', icon: Lock },
    { id: 'notifications' as const, label: 'Notifications', icon: Bell },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Profile Settings</h1>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Photo */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Profile Photo</h3>
              <div className="flex flex-col items-center">
                <div className="relative w-32 h-32 mb-4">
                  <img
                    src={photoPreview || profile?.profile_photo || 'https://via.placeholder.com/150'}
                    alt="Profile"
                    className="w-full h-full rounded-full object-cover border-4 border-gray-200"
                  />
                  <label
                    htmlFor="photo-upload"
                    className="absolute bottom-0 right-0 p-2 bg-blue-600 text-white rounded-full cursor-pointer hover:bg-blue-700"
                  >
                    <Camera className="w-4 h-4" />
                  </label>
                  <input
                    id="photo-upload"
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoChange}
                    className="hidden"
                  />
                </div>
                <p className="text-sm text-gray-500 text-center mb-4">
                  JPG, PNG or GIF (max 5MB)
                </p>
                {photoFile && (
                  <Button
                    onClick={handlePhotoUpload}
                    disabled={uploadPhotoMutation.isPending}
                    className="w-full"
                  >
                    {uploadPhotoMutation.isPending ? 'Uploading...' : 'Upload Photo'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Profile Form */}
          <Card className="lg:col-span-2">
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <Input
                      value={profileForm.full_name}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, full_name: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    <Input
                      type="email"
                      value={profileForm.email}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, email: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Phone</label>
                    <Input
                      value={profileForm.phone}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, phone: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Language</label>
                    <Select
                      value={profileForm.language}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, language: e.target.value })
                      }
                      options={[
                        { value: 'en', label: 'English' },
                        { value: 'ar', label: 'Arabic' },
                      ]}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Timezone</label>
                    <Select
                      value={profileForm.timezone}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, timezone: e.target.value })
                      }
                      options={[
                        { value: 'UTC', label: 'UTC' },
                        { value: 'Asia/Riyadh', label: 'Asia/Riyadh' },
                        { value: 'America/New_York', label: 'America/New_York' },
                        { value: 'Europe/London', label: 'Europe/London' },
                      ]}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Date Format</label>
                    <Select
                      value={profileForm.date_format}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, date_format: e.target.value })
                      }
                      options={[
                        { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
                        { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
                        { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
                      ]}
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button type="submit" disabled={updateProfileMutation.isPending}>
                    <Save className="w-4 h-4 mr-2" />
                    {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>
            <form onSubmit={handlePasswordSubmit} className="space-y-4 max-w-xl">
              <div>
                <label className="block text-sm font-medium mb-2">Current Password</label>
                <Input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, current_password: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">New Password</label>
                <Input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, new_password: e.target.value })
                  }
                  required
                />
                {passwordForm.new_password && (
                  <div className="mt-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Password Strength:</span>
                      <span className={`font-medium ${
                        passwordStrength.strength === 100 ? 'text-green-600' :
                        passwordStrength.strength === 75 ? 'text-blue-600' :
                        passwordStrength.strength === 50 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {passwordStrength.label}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${passwordStrength.color}`}
                        style={{ width: `${passwordStrength.strength}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Confirm New Password</label>
                <Input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, confirm_password: e.target.value })
                  }
                  required
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={changePasswordMutation.isPending}>
                  <Lock className="w-4 h-4 mr-2" />
                  {changePasswordMutation.isPending ? 'Changing...' : 'Change Password'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
            <form onSubmit={handleNotificationsSubmit} className="space-y-4 max-w-xl">
              <div className="space-y-3">
                <label className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <div>
                    <p className="font-medium">Email Notifications</p>
                    <p className="text-sm text-gray-500">Receive notifications via email</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationPrefs.email_notifications}
                    onChange={(e) =>
                      setNotificationPrefs({
                        ...notificationPrefs,
                        email_notifications: e.target.checked,
                      })
                    }
                    className="w-5 h-5 text-blue-600"
                  />
                </label>

                <label className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <div>
                    <p className="font-medium">SMS Notifications</p>
                    <p className="text-sm text-gray-500">Receive notifications via SMS</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationPrefs.sms_notifications}
                    onChange={(e) =>
                      setNotificationPrefs({
                        ...notificationPrefs,
                        sms_notifications: e.target.checked,
                      })
                    }
                    className="w-5 h-5 text-blue-600"
                  />
                </label>

                <label className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <div>
                    <p className="font-medium">Push Notifications</p>
                    <p className="text-sm text-gray-500">Receive in-app push notifications</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificationPrefs.push_notifications}
                    onChange={(e) =>
                      setNotificationPrefs({
                        ...notificationPrefs,
                        push_notifications: e.target.checked,
                      })
                    }
                    className="w-5 h-5 text-blue-600"
                  />
                </label>
              </div>

              <div className="flex justify-end">
                <Button type="submit" disabled={updateNotificationsMutation.isPending}>
                  <Save className="w-4 h-4 mr-2" />
                  {updateNotificationsMutation.isPending ? 'Saving...' : 'Save Preferences'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
