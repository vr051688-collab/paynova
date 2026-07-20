const express = require('express');
const Employee = require('../models/Employee');
const { requireAuth, requireAdmin } = require('../middleware/auth');

const router = express.Router();

// GET /api/employees - admin sees all, employee sees only their own record
router.get('/', requireAuth, async (req, res) => {
  try {
    if (req.user.role === 'admin') {
      const employees = await Employee.find().sort({ createdAt: -1 });
      return res.json(employees);
    }
    if (!req.user.employeeId) return res.json([]);
    const own = await Employee.findById(req.user.employeeId);
    res.json(own ? [own] : []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/employees - admin only
router.post('/', requireAuth, requireAdmin, async (req, res) => {
  try {
    const employee = new Employee(req.body);
    await employee.save();
    res.status(201).json(employee);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// PUT /api/employees/:id - admin only (update salary, department, add performance entry)
router.put('/:id', requireAuth, requireAdmin, async (req, res) => {
  try {
    const employee = await Employee.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(employee);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DELETE /api/employees/:id - admin only
router.delete('/:id', requireAuth, requireAdmin, async (req, res) => {
  try {
    await Employee.findByIdAndDelete(req.params.id);
    res.json({ success: true });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

module.exports = router;
