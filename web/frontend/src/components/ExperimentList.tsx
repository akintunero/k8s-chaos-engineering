interface Experiment {
  name: string
  status?: string
}

interface ExperimentListProps {
  experiments: Experiment[]
}

export default function ExperimentList({ experiments }: ExperimentListProps) {
  return (
    <div className="space-y-3">
      {experiments.map((exp) => (
        <div key={exp.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="h-2 w-2 bg-green-500 rounded-full mr-3"></div>
            <span className="font-medium text-gray-900">{exp.name}</span>
          </div>
          <span className="text-sm text-gray-500">{exp.status || 'Running'}</span>
        </div>
      ))}
    </div>
  )
}
