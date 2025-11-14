import { useLocation, useNavigate } from 'react-router-dom'
import './ReportPage.css'

const REPAIR_COSTS = {
  'damaged door': { min: 300, max: 1500, icon: '🚪' },
  'damaged window': { min: 200, max: 400, icon: '🪟' },
  'damaged headlight': { min: 200, max: 780, icon: '💡' },
  'damaged mirror': { min: 140, max: 330, icon: '🪞' },
  'dent': { min: 150, max: 600, icon: '🔨' },
  'damaged hood': { min: 300, max: 1500, icon: '🚗' },
  'damaged bumper': { min: 325, max: 1000, icon: '🛡️' },
  'damaged wind shield': { min: 200, max: 500, icon: '🪟' }
}

function ReportPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, originalImage } = location.state || {}

  if (!result) {
    navigate('/')
    return null
  }

  const calculateCost = (damageType) => {
    const cost = REPAIR_COSTS[damageType.toLowerCase()]
    if (!cost) return { min: 100, max: 500 }
    return cost
  }

  const totalCosts = result.classes?.reduce((acc, damage) => {
    const cost = calculateCost(damage)
    return {
      min: acc.min + cost.min,
      max: acc.max + cost.max
    }
  }, { min: 0, max: 0 }) || { min: 0, max: 0 }

  const downloadReport = () => {
    const link = document.createElement('a')
    link.href = result.annotated_image
    link.download = 'damage-report.png'
    link.click()
  }

  return (
    <div className="report-page">
      <div className="container">
        <header className="report-header">
          <button className="back-btn" onClick={() => navigate('/')}>
            ← Back to Upload
          </button>
          <h1>🔍 Damage Analysis Report</h1>
        </header>

        {result.classes && result.classes.length > 0 ? (
          <>
            <div className="images-grid">
              <div className="image-card">
                <h3>📷 Original Image</h3>
                <img src={originalImage} alt="Original" />
              </div>
              <div className="image-card">
                <h3>🎯 Detected Damage</h3>
                <img src={result.annotated_image} alt="Annotated" />
                <button className="download-btn" onClick={downloadReport}>
                  ⬇️ Download Report
                </button>
              </div>
            </div>

            <div className="cost-summary">
              <div className="summary-header">
                <h2>💰 Estimated Repair Cost</h2>
                <div className="total-cost">
                  ${totalCosts.min.toLocaleString()} - ${totalCosts.max.toLocaleString()}
                </div>
              </div>
              <p className="cost-note">
                Total estimated cost based on {result.classes.length} detected damage{result.classes.length > 1 ? 's' : ''}
              </p>
            </div>

            <div className="damages-list">
              <h3>📋 Detailed Breakdown</h3>
              {result.classes.map((damage, index) => {
                const cost = calculateCost(damage)
                const icon = REPAIR_COSTS[damage.toLowerCase()]?.icon || '🔧'
                return (
                  <div key={index} className="damage-item">
                    <div className="damage-info">
                      <span className="damage-icon">{icon}</span>
                      <div className="damage-details">
                        <h4>{damage}</h4>
                        <div className="confidence-bar">
                          <div 
                            className="confidence-fill" 
                            style={{ width: `${result.confidences[index]}%` }}
                          ></div>
                        </div>
                        <span className="confidence-text">
                          {result.confidences[index].toFixed(1)}% confidence
                        </span>
                      </div>
                    </div>
                    <div className="damage-cost">
                      <span className="cost-label">Estimated Repair</span>
                      <span className="cost-value">
                        ${cost.min} - ${cost.max}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="disclaimer">
              <h4>⚠️ Important Note</h4>
              <p>
                These are estimated repair costs based on industry averages. 
                Actual costs may vary depending on your location, vehicle make/model, 
                parts availability, and labor rates. We recommend getting quotes from 
                local repair shops for accurate pricing.
              </p>
            </div>
          </>
        ) : (
          <div className="no-damage">
            <div className="no-damage-icon">✅</div>
            <h2>Great News!</h2>
            <p>No damage detected on this vehicle</p>
            <img src={originalImage} alt="Original" className="no-damage-img" />
          </div>
        )}
      </div>
    </div>
  )
}

export default ReportPage
