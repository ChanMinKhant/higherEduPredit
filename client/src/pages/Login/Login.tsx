
import React, { useState } from 'react';
import { login } from '../../services/auth';

const Login: React.FC = () => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [message, setMessage] = useState('');

	const handleLogin = async (e: React.FormEvent) => {
		e.preventDefault();
		setMessage('');
		try {
			const response = await login({ email, password });
			console.log(response);
			setMessage('Login successful!');
		} catch (error) {
			setMessage('Invalid email or password.');
		}
	};

	return (
		<div>
			<h2>Login</h2>
			<form onSubmit={handleLogin}>
				<div>
					<label>Email:</label>
					<input
						type="email"
						value={email}
						onChange={e => setEmail(e.target.value)}
						required
					/>
				</div>
				<div>
					<label>Password:</label>
					<input
						type="password"
						value={password}
						onChange={e => setPassword(e.target.value)}
						required
					/>
				</div>
				<div>
					Don't have an account? <a href="/register">Register</a>	
				</div>
				<button type="submit">Login</button>
			</form>
			{message && <p>{message}</p>}
		</div>
	);
};

export default Login;
