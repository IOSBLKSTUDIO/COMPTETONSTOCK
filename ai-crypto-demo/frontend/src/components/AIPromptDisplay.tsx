import { useStore } from '../store/useStore'

export default function AIPromptDisplay() {
  const { aiPrompt, aiResponse, isGenerating } = useStore()

  if (!aiPrompt && !aiResponse) {
    return null
  }

  return (
    <div className="bg-dark-card rounded-xl p-6 border border-dark-border">
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-crypto-purple to-crypto-blue flex items-center justify-center">
          <span className="text-sm">AI</span>
        </div>
        <h2 className="text-lg font-semibold text-gray-300">AI Generation</h2>
        {isGenerating && (
          <div className="flex items-center space-x-1 text-crypto-green text-sm">
            <div className="w-2 h-2 rounded-full bg-crypto-green animate-pulse" />
            <span>Generating...</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {/* Prompt */}
        {aiPrompt && (
          <div>
            <div className="text-xs text-gray-500 mb-1">PROMPT</div>
            <div className="bg-dark-bg rounded-lg p-3 text-sm text-gray-300 font-mono">
              {aiPrompt}
            </div>
          </div>
        )}

        {/* Response */}
        {aiResponse && (
          <div>
            <div className="text-xs text-gray-500 mb-1">RESPONSE</div>
            <div className="bg-dark-bg rounded-lg p-3 text-sm font-mono max-h-48 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-crypto-green">
                {isGenerating ? (
                  <span className="typing-cursor">{aiResponse}</span>
                ) : (
                  aiResponse
                )}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
