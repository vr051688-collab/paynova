const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true, lowercase: true },
  password: { type: String, required: true }, // bcrypt hash
  role: { type: String, enum: ['admin', 'employee'], default: 'employee' },
  employeeId: { type: mongoose.Schema.Types.ObjectId, ref: 'Employee', default: null }
  resetOtp: { type: String, default: null },
  resetOtpExpires: { type: Date, default: null },
  }, { timestamps: true });
(empty)
module.exports = mongoose.model('User', userSchema);
