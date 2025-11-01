# Example 3: Writing an Installation Guide

## Problem Statement

Users are struggling to install your software. They encounter environment issues, missing dependencies, permission errors, and unclear instructions. You need a step-by-step installation guide that works for different platforms and skill levels.

## Use Case

Every software product needs clear installation instructions. Good installation guides reduce support burden, improve user success rate, and create positive first impressions.

## Solution Overview

Create a comprehensive installation guide covering prerequisites, platform-specific instructions, verification steps, troubleshooting, and next steps.

## Complete Installation Guide Example

```markdown
# Installation Guide

This guide will help you install [Product Name] on your system.

**Estimated time:** 15 minutes

## System Requirements

### Minimum Requirements
- **Operating System:** Windows 10+, macOS 11+, or Ubuntu 20.04+
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 500MB free space
- **Network:** Internet connection for initial setup

### Software Prerequisites
- **Python:** 3.9 or higher
- **pip:** 21.0 or higher
- **Git:** 2.25 or higher (optional, for source installation)

## Quick Install (Recommended)

For most users, use pip:

```bash
pip install product-name
```

Verify installation:

```bash
product-name --version
```

Expected output:
```
product-name version 2.0.0
```

✅ If you see the version number, installation was successful! → [Next Steps](#next-steps)

❌ If you encounter errors → [Troubleshooting](#troubleshooting)

## Detailed Installation Instructions

Choose your platform:
- [Windows](#windows)
- [macOS](#macos)
- [Linux](#linux)
- [Docker](#docker)

---

### Windows

#### Step 1: Install Python

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **Important:** Check "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

**Verify Python installation:**
```powershell
python --version
```

Expected output: `Python 3.9.x` or higher

#### Step 2: Install Product

Open Command Prompt (press Win+R, type `cmd`, press Enter):

```powershell
pip install product-name
```

#### Step 3: Verify Installation

```powershell
product-name --version
```

#### Troubleshooting Windows

**Issue: "'python' is not recognized"**

Solution:
1. Add Python to PATH manually
2. Search for "Environment Variables" in Start Menu
3. Edit "Path" variable
4. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python39`

**Issue: "Access denied"**

Solution: Run Command Prompt as Administrator

---

### macOS

#### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Python

```bash
brew install python@3.11
```

Verify:
```bash
python3 --version
```

#### Step 3: Install Product

```bash
pip3 install product-name
```

#### Step 4: Verify Installation

```bash
product-name --version
```

#### Troubleshooting macOS

**Issue: "command not found: product-name"**

Solution: Add Python bin to PATH:
```bash
echo 'export PATH="$HOME/Library/Python/3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Issue: "Permission denied"**

Solution: Install in user directory:
```bash
pip3 install --user product-name
```

---

### Linux

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install product
pip3 install product-name

# Verify
product-name --version
```

#### Fedora/CentOS/RHEL

```bash
# Install Python and pip
sudo dnf install python3 python3-pip -y

# Install product
pip3 install product-name

# Verify
product-name --version
```

#### Troubleshooting Linux

**Issue: "externally-managed-environment"**

Solution: Use virtual environment (recommended):
```bash
python3 -m venv myenv
source myenv/bin/activate
pip install product-name
```

Or use --break-system-packages (not recommended):
```bash
pip3 install --break-system-packages product-name
```

---

### Docker

#### Quick Start

```bash
docker pull product-name/product-name:latest
docker run -it product-name/product-name:latest
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  product:
    image: product-name/product-name:latest
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
    volumes:
      - ./data:/app/data
```

Run:
```bash
docker-compose up -d
```

---

## Advanced Installation

### From Source

```bash
# Clone repository
git clone https://github.com/user/product-name.git
cd product-name

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify
product-name --version
```

### Specific Version

```bash
# Install specific version
pip install product-name==1.5.0

# Install latest pre-release
pip install --pre product-name

# Upgrade to latest
pip install --upgrade product-name
```

## Configuration

### Initial Configuration

After installation, run the setup wizard:

```bash
product-name init
```

This will create a configuration file at:
- Windows: `C:\Users\YourName\.product\config.yml`
- macOS/Linux: `~/.product/config.yml`

### Manual Configuration

Create configuration file:

```yaml
# ~/.product/config.yml
api_key: "your-api-key-here"
base_url: "https://api.example.com"
timeout: 5000
log_level: "info"
```

Get your API key from [dashboard.example.com](https://dashboard.example.com)

## Verification

### Basic Test

```bash
product-name test
```

Expected output:
```
✓ Configuration loaded
✓ API connection successful
✓ Authentication working

All systems operational!
```

### Full System Check

```bash
product-name doctor
```

This checks:
- Python version compatibility
- Required dependencies
- Configuration validity
- Network connectivity
- API authentication

## Troubleshooting

### Common Issues

#### 1. Import Error

**Error:**
```
ImportError: No module named 'product_name'
```

**Solutions:**
1. Verify installation: `pip list | grep product-name`
2. Reinstall: `pip install --force-reinstall product-name`
3. Check Python version: `python --version` (must be 3.9+)

#### 2. Permission Errors

**Error:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solutions:**
1. Install for user only: `pip install --user product-name`
2. Use virtual environment (recommended)
3. Run as administrator/sudo (not recommended)

#### 3. SSL Certificate Error

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**
1. Update certificates: `pip install --upgrade certifi`
2. Check firewall/proxy settings
3. Contact IT department if on corporate network

#### 4. Version Conflicts

**Error:**
```
ERROR: product-name has requirement packageX>=2.0, but you have packageX 1.5
```

**Solutions:**
1. Upgrade conflicting package: `pip install --upgrade packageX`
2. Use virtual environment to isolate dependencies
3. Check compatibility matrix in documentation

### Getting Help

If you're still having issues:

1. **Check documentation:** [docs.example.com](https://docs.example.com)
2. **Search existing issues:** [github.com/user/repo/issues](https://github.com/user/repo/issues)
3. **Ask community:** [community.example.com](https://community.example.com)
4. **Report bug:** [github.com/user/repo/issues/new](https://github.com/user/repo/issues/new)
5. **Contact support:** support@example.com

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- pip version (`pip --version`)
- Full error message
- Installation method used

## Next Steps

Now that you have [Product Name] installed:

1. **Configure:** Set up your API key and preferences
   ```bash
   product-name config set api_key "YOUR_KEY"
   ```

2. **Learn basics:** Follow the [Quick Start Guide](../quickstart.md)

3. **Try examples:** Explore [example projects](../examples/)

4. **Read docs:** Browse the [full documentation](https://docs.example.com)

## Uninstallation

To remove [Product Name]:

```bash
# Uninstall
pip uninstall product-name

# Remove configuration (optional)
# Windows:
rmdir /s %USERPROFILE%\.product
# macOS/Linux:
rm -rf ~/.product
```

## Frequently Asked Questions

**Q: Can I install multiple versions?**
A: Yes, use virtual environments for each version.

**Q: Do I need admin/sudo rights?**
A: No, use `pip install --user` or virtual environments.

**Q: How do I upgrade to the latest version?**
A: Run `pip install --upgrade product-name`

**Q: Can I install without internet?**
A: Yes, download the wheel file and install offline: `pip install product-name-2.0.0-py3-none-any.whl`

**Q: Is it safe to install?**
A: Yes, the package is verified and scanned. Check [security policy](https://github.com/user/repo/security).

---

**Installation successful?** → Start with the [Quick Start Guide](../quickstart.md)

**Having problems?** → Check [Troubleshooting](#troubleshooting) or [get help](#getting-help)
```

## Key Elements

1. **Clear prerequisites upfront**
2. **Quick install option first**
3. **Platform-specific instructions**
4. **Verification steps**
5. **Comprehensive troubleshooting**
6. **Multiple installation methods**
7. **Next steps after installation**

## Benefits

- **Reduces support tickets:** Common issues addressed upfront
- **Improves success rate:** Step-by-step instructions with verification
- **Builds confidence:** Users know they installed correctly
- **Saves time:** Quick install for experienced users, detailed for beginners

## Related Examples

- [README File](readme-file.md): Project overview
- [Configuration Guide](../intermediate/configuration-guide.md): Setting up after install
- [Quick Start Guide](../intermediate/quickstart-guide.md): First steps after install
