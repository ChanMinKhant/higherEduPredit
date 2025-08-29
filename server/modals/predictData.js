import { Schema, model } from 'mongoose';

const userSchema = new Schema({
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    
}, { timestamps: true });

export default model('User', userSchema);