// Deployment helper script
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ensure we're in the frontend directory
const frontendDir = __dirname;

console.log('Starting deployment process...');

try {
  // Run the production build
  console.log('Building for production...');
  execSync('npm run build:prod', { stdio: 'inherit', cwd: frontendDir });
  
  // Check if Vercel CLI is installed
  try {
    execSync('vercel --version', { stdio: 'pipe' });
    console.log('Vercel CLI is installed. Deploying to Vercel...');
    
    // Deploy to Vercel
    const deployCommand = process.argv.includes('--prod') ? 'vercel --prod' : 'vercel';
    execSync(deployCommand, { stdio: 'inherit', cwd: frontendDir });
    
    console.log('Deployment completed successfully!');
  } catch (vercelError) {
    console.log('Vercel CLI is not installed or not in PATH.');
    console.log('To deploy to Vercel, please:');
    console.log('1. Install Vercel CLI: npm install -g vercel');
    console.log('2. Run: vercel --prod');
    console.log('\nAlternatively, you can deploy the dist folder manually to your hosting provider.');
  }
} catch (error) {
  console.error('Deployment failed:', error);
}