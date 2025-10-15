// Production build script
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ensure we're in the frontend directory
const frontendDir = __dirname;

// Backup the current .env file
const envPath = path.join(frontendDir, '.env');
const envBackupPath = path.join(frontendDir, '.env.backup');

if (fs.existsSync(envPath)) {
  console.log('Backing up current .env file...');
  fs.copyFileSync(envPath, envBackupPath);
}

// Create production .env file
console.log('Creating production .env file...');
fs.writeFileSync(
  envPath,
  '# API Configuration\n' +
  '# VITE_API_BASE_URL=http://localhost:8000\n' +
  '# For production deployment\n' +
  'VITE_API_BASE_URL=https://smart-resume-screener-jee0.onrender.com\n'
);

try {
  // Run the build
  console.log('Building for production...');
  execSync('npm run build', { stdio: 'inherit', cwd: frontendDir });
  console.log('Production build completed successfully!');
} catch (error) {
  console.error('Build failed:', error);
} finally {
  // Restore the original .env file
  if (fs.existsSync(envBackupPath)) {
    console.log('Restoring original .env file...');
    fs.copyFileSync(envBackupPath, envPath);
    fs.unlinkSync(envBackupPath);
  }
}

console.log('Build process completed!');