const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  type: { type: String, enum: ['income', 'expense'], required: true },
  category: { type: String, required: true }, // e.g. "Sales", "Rent", "Software"
  amount: { type: Number, required: true },
  date: { type: Date, default: Date.now },
  description: { type: String, default: '' }
}, { timestamps: true });

module.exports = mongoose.model('Transaction', transactionSchema);
