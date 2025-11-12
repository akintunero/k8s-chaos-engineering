import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Experiments from './components/Experiments'
import Schedules from './components/Schedules'
import Layout from './components/Layout'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/experiments" element={<Experiments />} />
          <Route path="/schedules" element={<Schedules />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
