import { useEffect, useState } from 'react'
import { Play, Square, RefreshCw, AlertCircle } from 'lucide-react'
import { api } from '../services/api'

interface Experiment {
  name: string
  status?: string
}

export default function Experiments() {
  const [experiments, setExperiments] = useState<string[]>([])
  const [running, setRunning] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null)

  useEffect(() => {
    loadExperiments()
    const interval = setInterval(loadExperiments, 3000)
    return () => clearInterval(interval)
  }, [])

  const loadExperiments = async () => {
    try {
      const [available, runningData] = await Promise.all([
        api.getExperiments(),
        api.getRunningExperiments()
      ])
      setExperiments(available.experiments || [])
      setRunning(runningData.running?.map((e: any) => e.name) || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading experiments:', error)
      setLoading(false)
    }
  }

  const handleRun = async (name: string) => {
    try {
      await api.runExperiment(name)
      setSelectedExperiment(name)
      setTimeout(loadExperiments, 1000)
    } catch (error) {
      console.error('Error running experiment:', error)
      alert('Failed to run experiment')
    }
  }

  const handleStop = async (name: string) => {
    try {
      await api.stopExperiment(name)
      setTimeout(loadExperiments, 1000)
    } catch (error) {
      console.error('Error stopping experiment:', error)
      alert('Failed to stop experiment')
    }
  }

  const isRunning = (name: string) => running.includes(name)

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
        <h1 className="text-3xl font-bold text-gray-900">Experiments</h1>
        <p className="mt-2 text-sm text-gray-600">
          Run and manage chaos engineering experiments
        </p>
      </div>

      {experiments.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-8 text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-gray-500">No experiments available</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:p-6">
            <div className="space-y-4">
              {experiments.map((exp) => (
                <div
                  key={exp}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      {isRunning(exp) ? (
                        <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                      ) : (
                        <div className="h-3 w-3 bg-gray-300 rounded-full"></div>
                      )}
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">{exp}</h3>
                      <p className="text-sm text-gray-500">
                        {isRunning(exp) ? 'Running' : 'Available'}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    {isRunning(exp) ? (
                      <>
                        <button
                          onClick={() => handleStop(exp)}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                          <Square className="h-4 w-4 mr-2" />
                          Stop
                        </button>
                        <button
                          onClick={() => api.getExperimentStatus(exp)}
                          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                        >
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Status
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => handleRun(exp)}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Run
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
