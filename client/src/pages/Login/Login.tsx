
// import React, { useState } from 'react';
// import { login } from '../../services/auth';

// const Login: React.FC = () => {
// 	const [email, setEmail] = useState('');
// 	const [password, setPassword] = useState('');
// 	const [message, setMessage] = useState('');

// 	const handleLogin = async (e: React.FormEvent) => {
// 		e.preventDefault();
// 		setMessage('');
// 		try {
// 			const response = await login({ email, password });
// 			console.log(response);
// 			setMessage('Login successful!');
// 		} catch (error) {
// 			setMessage('Invalid email or password.');
// 		}
// 	};

// 	return (
// 		<div className=''>
// 			<h2 className="text-2xl font-bold text-center text-[#9c23d9] mt-8 mb-6">Login</h2>
// 			<div className="w-[150px] h-1 m-auto bg-[#9c23d9] mt-[-20px] rounded text-center"></div>
// 			<form onSubmit={handleLogin}>
// 				<div>
// 					<label className="block text-gray-600 font-medium mb-1">Email:</label>
// 					<input
// 						type="email"
// 						value={email}
// 						onChange={e => setEmail(e.target.value)}
// 						required
// 						className="w-full px-4 py-8 h-[40px] rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
// 					/>
// 				</div>
// 				<div>
// 					<label className="block text-gray-600 font-medium mb-1">Password:</label>
// 					<input
// 						type="password"
// 						value={password}
// 						onChange={e => setPassword(e.target.value)}
// 						required
// 						className="w-full px-4 py-8 h-[40px] rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
// 					/>
// 				</div>
// 				<div>
// 					Don't have an account? <a href="/register">Register</a>	
// 				</div>
// 				<button type="submit">Login</button>
// 			</form>
// 			{message && <p>{message}</p>}
// 		</div>
// 	);
// };

// export default Login;
import React, { useEffect, useState } from "react";
import { login } from "../../services/auth";
import { useNavigate } from "react-router-dom";
import { useUser } from "../../hooks/useUser";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  // Assuming getUser is a hook or function that returns user and loading
  const { user, loading } = useUser();

  useEffect(() => {
    if (!loading && user) {
      // If user already logged in / exists → redirect
      navigate("/predict");
    }
  }, [user, loading, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    try {
      const response = await login({ email, password });
      setMessage("✅ Login successful!");
      window.location.href = '/predict'; // Redirect to home page after successful login
    } catch (error) {
      setMessage("❌ Invalid email or password.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
       <div className="absolute inset-0 bg-[url('/bg.jpg')] bg-cover bg-center blur-sm -z-10"></div>
        <div className="w-full max-w-md  rounded-2xl bg-white shadow-lg h-[400px] pb-6">
        <form
      onSubmit={handleLogin}
      className="flex flex-col items-center w-full p-16 justify-evenly h-full"
    >
          <h2 className="text-2xl font-bold text-center text-[#9c23d9] mt-8 mb-6">
            Login
          </h2>
          <div className="w-[150px] h-1 m-auto bg-[#9c23d9] mt-[-20px] rounded"></div>

          <div className="mb-4 w-[90%]">
            <label className="block text-gray-600 font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 h-[40px] rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="mb-6 w-[90%]">
            <label className="block text-gray-600 font-medium mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 h-[40px] rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            className="w-[120px] py-[10px] h-[40px] bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
          >
            Login
          </button>
        <p className="mt-6 text-center text-gray-600 text-sm">
          Don&apos;t have an account?{" "}
          <a
            href="/register"
            className="text-blue-600 font-medium hover:underline"
          >
            Register
          </a>
        </p>
        {message && (
          <p
            className={`mt-4 text-center font-medium ${
              message.includes("successful") ? "text-green-600" : "text-red-600"
            }`}
          >
            {message}
          </p>
        )}
        </form>


      </div>
    </div>
  );
};

export default Login;
