import { useEffect, useState } from 'react'
import { Play, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { api } from '../services/api'
import MetricCard from './MetricCard'
import ExperimentList from './ExperimentList'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalExperiments: 0,
    runningExperiments: 0,
    scheduledExperiments: 0,
    successRate: 0
  })
  const [recentExperiments, setRecentExperiments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadDashboardData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const [experiments, running, schedules] = await Promise.all([
        api.getExperiments(),
        api.getRunningExperiments(),
        api.getSchedules()
      ])

      setStats({
        totalExperiments: experiments.experiments?.length || 0,
        runningExperiments: running.running?.length || 0,
        scheduledExperiments: schedules.schedules?.length || 0,
        successRate: 95 // Placeholder
      })

      setRecentExperiments(running.running || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      setLoading(false)
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor and manage your chaos engineering experiments
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <MetricCard
          title="Total Experiments"
          value={stats.totalExperiments}
          icon={Play}
          color="blue"
        />
        <MetricCard
          title="Running"
          value={stats.runningExperiments}
          icon={Clock}
          color="yellow"
        />
        <MetricCard
          title="Scheduled"
          value={stats.scheduledExperiments}
          icon={Clock}
          color="purple"
        />
        <MetricCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          icon={CheckCircle}
          color="green"
        />
      </div>

      {/* Recent Experiments */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Experiments</h2>
          {recentExperiments.length > 0 ? (
            <ExperimentList experiments={recentExperiments} />
          ) : (
            <div className="text-center py-8 text-gray-500">
              <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">No running experiments</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
