// Run once with: node seed.js
// Creates an admin login, a sample employee login, and demo data.
require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('./models/User');
const Employee = require('./models/Employee');
const Transaction = require('./models/Transaction');

async function seed() {
  await mongoose.connect(process.env.MONGO_URI);
  console.log('Connected to MongoDB. Seeding...');

  // --- Admin account ---
  const adminEmail = 'admin@payroll.com';
  const adminPassword = 'Admin@123'; // change after first login
  let adminUser = await User.findOne({ email: adminEmail });
  if (!adminUser) {
    const hashed = await bcrypt.hash(adminPassword, 10);
    adminUser = await User.create({ name: 'Admin', email: adminEmail, password: hashed, role: 'admin' });
    console.log(`Admin created -> email: ${adminEmail}  password: ${adminPassword}`);
  } else {
    console.log('Admin already exists, skipping.');
  }

  // --- Sample employees ---
  const sampleEmployees = [
    { name: 'Aizen Varun', email: 'varun@company.com', salary: 45000, department: 'Engineering', position: 'Full Stack Developer', performanceHistory: [{ month: '2026-04', score: 78 }, { month: '2026-05', score: 82 }, { month: '2026-06', score: 88 }] },
    { name: 'Priya Sharma', email: 'priya@company.com', salary: 52000, department: 'Engineering', position: 'Backend Developer', performanceHistory: [{ month: '2026-04', score: 85 }, { month: '2026-05', score: 80 }, { month: '2026-06', score: 90 }] },
    { name: 'Rahul Nair', email: 'rahul@company.com', salary: 38000, department: 'Marketing', position: 'Marketing Executive', performanceHistory: [{ month: '2026-04', score: 70 }, { month: '2026-05', score: 75 }, { month: '2026-06', score: 72 }] },
    { name: 'Sneha Gowda', email: 'sneha@company.com', salary: 41000, department: 'HR', position: 'HR Associate', performanceHistory: [{ month: '2026-04', score: 88 }, { month: '2026-05', score: 91 }, { month: '2026-06', score: 89 }] }
  ];

  for (const emp of sampleEmployees) {
    const exists = await Employee.findOne({ email: emp.email });
    if (!exists) await Employee.create(emp);
  }
  console.log('Sample employees ensured.');

  // --- Sample employee login (linked to first employee) ---
  const firstEmployee = await Employee.findOne({ email: 'varun@company.com' });
  const empLoginEmail = 'varun@company.com';
  let empUser = await User.findOne({ email: empLoginEmail });
  if (!empUser && firstEmployee) {
    const hashed = await bcrypt.hash('Employee@123', 10);
    empUser = await User.create({
      name: firstEmployee.name,
      email: empLoginEmail,
      password: hashed,
      role: 'employee',
      employeeId: firstEmployee._id
    });
    console.log(`Employee login created -> email: ${empLoginEmail}  password: Employee@123`);
  }

  // --- Sample income/expense transactions ---
  const sampleTransactions = [
    { type: 'income', category: 'Client Project', amount: 250000, description: 'Payroll dashboard contract' },
    { type: 'income', category: 'Consulting', amount: 80000, description: 'Consulting retainer' },
    { type: 'expense', category: 'Office Rent', amount: 45000, description: 'Monthly rent' },
    { type: 'expense', category: 'Software Tools', amount: 12000, description: 'SaaS subscriptions' },
    { type: 'expense', category: 'Marketing', amount: 20000, description: 'Ad campaign' }
  ];
  const txnCount = await Transaction.countDocuments();
  if (txnCount === 0) {
    await Transaction.insertMany(sampleTransactions);
    console.log('Sample transactions inserted.');
  }

  console.log('Seeding complete.');
  process.exit(0);
}

seed().catch(err => {
  console.error(err);
  process.exit(1);
});
