const mongoose = require('mongoose');

const employeeSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  salary: { type: Number, required: true },
  department: { type: String, default: 'General' },
  position: { type: String, default: 'Staff' },
  joinDate: { type: Date, default: Date.now },
  performanceHistory: [
    {
      month: String, // e.g. "2026-06"
      score: Number  // 0-100
    }
  ]
}, { timestamps: true });

module.exports = mongoose.model('Employee', employeeSchema);
