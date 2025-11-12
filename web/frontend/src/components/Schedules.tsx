import { useEffect, useState } from 'react'
import { Plus, Trash2, Clock } from 'lucide-react'
import { api } from '../services/api'

interface Schedule {
  name: string
  schedule: string
  last_run?: string
  active?: number
}

export default function Schedules() {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    experiment: '',
    schedule: ''
  })

  useEffect(() => {
    loadSchedules()
    const interval = setInterval(loadSchedules, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadSchedules = async () => {
    try {
      const data = await api.getSchedules()
      setSchedules(data.schedules || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading schedules:', error)
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.createSchedule(formData.experiment, formData.schedule)
      setShowForm(false)
      setFormData({ experiment: '', schedule: '' })
      loadSchedules()
    } catch (error) {
      console.error('Error creating schedule:', error)
      alert('Failed to create schedule')
    }
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`Delete schedule for ${name}?`)) return
    try {
      await api.deleteSchedule(name)
      loadSchedules()
    } catch (error) {
      console.error('Error deleting schedule:', error)
      alert('Failed to delete schedule')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scheduled Experiments</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage automated chaos experiment schedules
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Schedule
        </button>
      </div>

      {showForm && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Create Schedule</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Experiment</label>
              <input
                type="text"
                value={formData.experiment}
                onChange={(e) => setFormData({ ...formData, experiment: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                placeholder="pod-delete"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Cron Schedule</label>
              <input
                type="text"
                value={formData.schedule}
                onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                placeholder="0 2 * * *"
                required
              />
              <p className="mt-1 text-sm text-gray-500">Format: minute hour day month weekday</p>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        {schedules.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Clock className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2">No scheduled experiments</p>
          </div>
        ) : (
          <div className="px-4 py-5 sm:p-6">
            <div className="space-y-4">
              {schedules.map((schedule) => (
                <div
                  key={schedule.name}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{schedule.name}</h3>
                    <p className="text-sm text-gray-500">Schedule: {schedule.schedule}</p>
                    {schedule.last_run && (
                      <p className="text-xs text-gray-400">Last run: {schedule.last_run}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(schedule.name)}
                    className="inline-flex items-center px-3 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
