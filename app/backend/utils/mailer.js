const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD,
  },
});

async function sendOtpEmail(to, otp) {
  await transporter.sendMail({
    from: `"Paynova" <${process.env.GMAIL_USER}>`,
    to,
    subject: 'Your Password Reset OTP',
    html: `<p>Your OTP code is:</p><h2>${otp}</h2><p>This code expires in 10 minutes.</p>`,
  });
}

module.exports = { sendOtpEmail };
