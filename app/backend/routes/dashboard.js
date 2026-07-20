const express = require('express');
const Employee = require('../models/Employee');
const Transaction = require('../models/Transaction');
const { requireAuth, requireAdmin } = require('../middleware/auth');

const router = express.Router();

// GET /api/dashboard/department-cost - admin only
// Total salary cost grouped by department
router.get('/department-cost', requireAuth, requireAdmin, async (req, res) => {
  try {
    const result = await Employee.aggregate([
      { $group: { _id: '$department', totalCost: { $sum: '$salary' }, headcount: { $sum: 1 } } },
      { $sort: { totalCost: -1 } }
    ]);
    res.json(result.map(r => ({ department: r._id || 'General', totalCost: r.totalCost, headcount: r.headcount })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/dashboard/profit-stats - admin only
// Total income, total expenses, total payroll cost, net profit
router.get('/profit-stats', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [incomeAgg] = await Transaction.aggregate([
      { $match: { type: 'income' } },
      { $group: { _id: null, total: { $sum: '$amount' } } }
    ]);
    const [expenseAgg] = await Transaction.aggregate([
      { $match: { type: 'expense' } },
      { $group: { _id: null, total: { $sum: '$amount' } } }
    ]);
    const [payrollAgg] = await Employee.aggregate([
      { $group: { _id: null, total: { $sum: '$salary' } } }
    ]);

    const totalIncome = incomeAgg?.total || 0;
    const totalExpenses = expenseAgg?.total || 0;
    const totalPayroll = payrollAgg?.total || 0;
    const netProfit = totalIncome - totalExpenses - totalPayroll;

    res.json({ totalIncome, totalExpenses, totalPayroll, netProfit });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/dashboard/performance - admin sees all employees, employee sees own history
router.get('/performance', requireAuth, async (req, res) => {
  try {
    if (req.user.role === 'admin') {
      const employees = await Employee.find().select('name department performanceHistory');
      return res.json(employees);
    }
    if (!req.user.employeeId) return res.json([]);
    const own = await Employee.findById(req.user.employeeId).select('name department performanceHistory');
    res.json(own ? [own] : []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
