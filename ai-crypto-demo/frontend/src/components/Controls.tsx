import { useState } from 'react'
import { useStore } from '../store/useStore'

export default function Controls() {
  const {
    cryptoId,
    simulationStatus,
    isGenerating,
    generateWithAI,
    startSimulation,
    stopSimulation,
    reset,
  } = useStore()

  const [duration, setDuration] = useState(60)
  const [intensity, setIntensity] = useState('medium')

  const handleGenerate = async () => {
    try {
      await generateWithAI(['stable price', 'fair distribution'])
    } catch (error) {
      console.error('Generation failed:', error)
    }
  }

  const handleStartSimulation = async () => {
    try {
      await startSimulation(duration, intensity)
    } catch (error) {
      console.error('Start simulation failed:', error)
    }
  }

  return (
    <div className="bg-dark-card rounded-xl p-6 border border-dark-border">
      <div className="flex flex-wrap items-center gap-4">
        {/* Generate Button */}
        {!cryptoId && (
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className={`
              px-6 py-3 rounded-lg font-semibold transition-all
              ${
                isGenerating
                  ? 'bg-gray-700 cursor-not-allowed'
                  : 'bg-gradient-to-r from-crypto-blue to-crypto-purple hover:opacity-90'
              }
            `}
          >
            {isGenerating ? (
              <span className="flex items-center space-x-2">
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                <span>AI Generating...</span>
              </span>
            ) : (
              'Generate Crypto with AI'
            )}
          </button>
        )}

        {/* Simulation Controls */}
        {cryptoId && (
          <>
            {/* Duration Select */}
            <div className="flex items-center space-x-2">
              <label className="text-gray-400 text-sm">Duration:</label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                disabled={simulationStatus === 'running'}
                className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
              >
                <option value={30}>30s</option>
                <option value={60}>60s</option>
                <option value={120}>120s</option>
              </select>
            </div>

            {/* Intensity Select */}
            <div className="flex items-center space-x-2">
              <label className="text-gray-400 text-sm">Intensity:</label>
              <select
                value={intensity}
                onChange={(e) => setIntensity(e.target.value)}
                disabled={simulationStatus === 'running'}
                className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            {/* Start/Stop Button */}
            {simulationStatus !== 'running' ? (
              <button
                onClick={handleStartSimulation}
                className="px-6 py-3 rounded-lg font-semibold bg-crypto-green text-black hover:bg-crypto-green/90 transition-all"
              >
                Start Simulation
              </button>
            ) : (
              <button
                onClick={stopSimulation}
                className="px-6 py-3 rounded-lg font-semibold bg-crypto-red hover:bg-crypto-red/90 transition-all"
              >
                Stop
              </button>
            )}

            {/* Reset Button */}
            <button
              onClick={reset}
              disabled={simulationStatus === 'running'}
              className="px-4 py-3 rounded-lg font-semibold border border-dark-border hover:bg-dark-border transition-all disabled:opacity-50"
            >
              Reset
            </button>
          </>
        )}
      </div>

      {/* Progress Bar */}
      {simulationStatus === 'running' && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>Simulation Progress</span>
            <span>{Math.round(useStore.getState().simulationProgress * 100)}%</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2">
            <div
              className="bg-gradient-to-r from-crypto-blue to-crypto-green h-2 rounded-full transition-all duration-300"
              style={{ width: `${useStore.getState().simulationProgress * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
