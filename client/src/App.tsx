import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import AdminPanel from './pages/AdminPanel/AdminPanel';
import Navbar from './components/Navbar';
import Register from './pages/Register/Register';
import Login from './pages/Login/Login';
import PredictionForm from './pages/PredictionForm/PredictionForm';
import RecentPrediction from './pages/RecentPrediction/RecentPrediction';
import UserManage from './pages/UserManage/UserMange';
import { Bounce, ToastContainer } from 'react-toastify';

function App() {

  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<div>Home</div>} />
            
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/predict" element={<PredictionForm />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/predictions" element={<RecentPrediction />} />
            <Route path="/predictions/:userid" element={<RecentPrediction />} />
            <Route path="/users" element={<UserManage />} />
            <Route path="*" element={<h1>404 - Not Found</h1>} />
          </Routes>
          <ToastContainer
            position="top-center"
            autoClose={3500}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick={false}
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
            transition={Bounce}
          />

        </main>
      </div>

    </Router>
  );
}

export default App;