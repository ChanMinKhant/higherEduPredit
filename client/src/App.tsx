import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import AdminPanel from './pages/AdminPanel/AdminPanel';
import Navbar from './components/Navbar';
import Register from './pages/Register/Register';
import Login from './pages/Login/Login';
import PredictionForm from './pages/PredictionForm/PredictionForm';
import RecentPrediction from './pages/RecentPrediction/RecentPrediction';
import UserManage from './pages/UserManage/UserMange';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<PredictionForm />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/predictions" element={<RecentPrediction />} />
            <Route path="/users" element={<UserManage />} />
            <Route path="*" element={<h1>404 - Not Found</h1>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;