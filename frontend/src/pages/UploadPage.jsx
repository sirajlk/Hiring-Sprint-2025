import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './UploadPage.css'

function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setLoading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post('/api/detection', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      navigate('/report', { 
        state: { 
          result: response.data,
          originalImage: preview
        } 
      })
    } catch (error) {
      console.error('Error analyzing image:', error)
      alert('Error analyzing image. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="container">
        <header className="header">
          <h1>🚗 AI Car Damage Detection</h1>
          <p>Upload a photo to instantly detect and analyze vehicle damage</p>
        </header>

        <div className="main-card">
          <div
            className={`upload-section ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {!preview ? (
              <>
                <div className="upload-icon">📸</div>
                <h2>Select or Drag & Drop an Image</h2>
                <p>Support for JPG, PNG images</p>
                <label htmlFor="fileInput" className="file-label">
                  Choose Image
                </label>
                <input
                  id="fileInput"
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                  style={{ display: 'none' }}
                />
              </>
            ) : (
              <div className="preview-section">
                <img src={preview} alt="Preview" className="preview-image" />
                <div className="preview-actions">
                  <button
                    className="change-btn"
                    onClick={() => {
                      setSelectedFile(null)
                      setPreview(null)
                    }}
                  >
                    Change Image
                  </button>
                  <button
                    className="analyze-btn"
                    onClick={handleAnalyze}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="loader"></span>
                        Analyzing...
                      </>
                    ) : (
                      'Analyze Damage'
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadPage
