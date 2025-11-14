import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import ReportPage from './pages/ReportPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/report" element={<ReportPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
