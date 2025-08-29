import dotenv from 'dotenv';
dotenv.config({ path: './config.env' });
import express from 'express';
import mongoose from 'mongoose';
import routes from './routes/index.js';
import cors from 'cors';

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(cors(
    {
        origin: 'http://localhost:5173',
        credentials: true,
    }
));

// db connect
mongoose.connect(process.env.MONGO_URI, {
}).then(() => {
    console.log('MongoDB connected');
}).catch(err => {
    console.error('MongoDB connection error:', err);
});

app.use('/api', routes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
