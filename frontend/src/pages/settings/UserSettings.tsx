import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spinner } from '@/components/ui/Spinner'

export default function UserSettings() {
  const navigate = useNavigate()

  useEffect(() => {
    // Redirect to Profile page since user settings are the same as profile settings
    navigate('/settings/profile', { replace: true })
  }, [navigate])

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <Spinner />
        <p className="mt-4 text-gray-600">Redirecting to Profile Settings...</p>
      </div>
    </div>
  )
}
