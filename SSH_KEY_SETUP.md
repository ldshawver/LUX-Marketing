# SSH Key Setup Guide

This guide explains how to set up SSH keys for GitHub access on your development machine.

## Quick Start

### Using the Automated Script

The easiest way to add your SSH key to GitHub is using the provided script:

```bash
./setup-ssh-key.sh
```

This will:
1. Check if GitHub CLI is installed and authenticated
2. Look for your SSH key at `~/.ssh/id_ed25519_luxit.pub`
3. Add it to GitHub with a title like "Mac Studio luxit 2026-01-22"

### Custom SSH Key Path

If your SSH key is in a different location:

```bash
./setup-ssh-key.sh /path/to/your/key.pub "Your Machine Name"
```

## Manual Setup

If you prefer to add the SSH key manually:

```bash
gh ssh-key add ~/.ssh/id_ed25519_luxit.pub --title "Mac Studio luxit $(date +%F)"
```

## Prerequisites

### 1. Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Ubuntu/Debian:**
```bash
sudo apt install gh
```

**Other systems:**
Visit [https://cli.github.com/](https://cli.github.com/)

### 2. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

### 3. Generate SSH Key (if needed)

If you don't have an SSH key yet:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_luxit
```

This creates:
- Private key: `~/.ssh/id_ed25519_luxit`
- Public key: `~/.ssh/id_ed25519_luxit.pub`

**Important:** Never share your private key!

### 4. Add SSH Key to SSH Agent

```bash
# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your SSH key
ssh-add ~/.ssh/id_ed25519_luxit
```

### 5. Configure SSH for GitHub

Create or edit `~/.ssh/config`:

```
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_luxit
    AddKeysToAgent yes
```

## Verification

Test your SSH connection to GitHub:

```bash
ssh -T git@github.com
```

You should see a message like:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## Troubleshooting

### "gh: command not found"
Install GitHub CLI (see Prerequisites above).

### "You need to authenticate with GitHub CLI first"
Run `gh auth login` and follow the prompts.

### "SSH key not found"
Generate a new SSH key (see step 3 above) or specify the correct path.

### "Permission denied (publickey)"
Make sure:
1. Your SSH key is added to GitHub
2. The SSH agent is running
3. Your key is added to the agent: `ssh-add ~/.ssh/id_ed25519_luxit`

## Security Best Practices

1. **Use different SSH keys** for different machines/purposes
2. **Add a passphrase** to your SSH key for extra security
3. **Regularly review** your SSH keys at [https://github.com/settings/keys](https://github.com/settings/keys)
4. **Remove old keys** from machines you no longer use
5. **Never commit** private keys to repositories

## Managing Your SSH Keys

View all SSH keys on your GitHub account:
```bash
gh ssh-key list
```

Remove an SSH key:
```bash
gh ssh-key delete <key-id>
```

Or manage them via the web interface: [https://github.com/settings/keys](https://github.com/settings/keys)

## Additional Resources

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [SSH Key Best Practices](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
