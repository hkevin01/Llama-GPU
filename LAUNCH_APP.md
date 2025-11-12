# 🚀 How to Launch Your App

## Three Ways to Launch

### 1️⃣ Applications Menu (Recommended)

```
┌─────────────────────────────────────┐
│  Press Super Key (⊞ Windows Key)    │
│                                     │
│  Type: "Llama GPU"                  │
│                                     │
│  Click: 📱 Llama GPU Assistant      │
└─────────────────────────────────────┘
```

**That's it!** Your app will open.

---

### 2️⃣ Command Line

```bash
cd /home/kevin/Projects/Llama-GPU
./bin/llama-assistant
```

---

### 3️⃣ Desktop File Launcher

```bash
gtk-launch llama-gpu-assistant
```

---

## 📍 Where to Find It

Your app appears in these locations:

### GNOME (Ubuntu Default)
- Press `Super` → Type "Llama"
- Activities → Show Applications → Search "Llama"
- Under categories: **Utilities** or **Development**

### Unity
- Click Dash → Type "Llama"
- Or find in: Applications → Accessories → Llama GPU Assistant

### System Menu
Look for **Llama GPU Assistant** with the GPU chip icon 🖥️

---

## ⭐ Add to Favorites

1. Find "Llama GPU Assistant" in applications
2. Right-click the icon
3. Select **"Add to Favorites"**
4. Now it's always in your dock!

---

## ⌨️ Create Keyboard Shortcut (Optional)

### GNOME/Ubuntu:
1. Open **Settings**
2. Go to **Keyboard** → **Keyboard Shortcuts**
3. Scroll to bottom → Click **"+"** (Add Custom Shortcut)
4. Fill in:
   - **Name**: `Llama GPU Assistant`
   - **Command**: `/home/kevin/Projects/Llama-GPU/bin/llama-assistant`
   - **Shortcut**: Press `Ctrl+Alt+L` (or your choice)
5. Click **Add**

Now press `Ctrl+Alt+L` anytime to launch!

---

## 🎨 The App Icon

Look for this icon in your menu:

```
🟣 Purple circle background
🖤 Black GPU chip with circuit lines
💗 Pink AI brain waves
💚 Green glowing core
⚡ Gold lightning bolts
```

Symbolizes: **AI + GPU + Power** ⚡

---

## 🔍 Can't Find It?

### Solution 1: Refresh Desktop Database
```bash
update-desktop-database ~/.local/share/applications
```

### Solution 2: Log Out & Back In
Sometimes desktop environments cache the app list.

### Solution 3: Verify Installation
```bash
ls ~/.local/share/applications/llama-gpu-assistant.desktop
ls ~/.local/share/icons/llama-assistant.svg
```

Both files should exist.

---

## �� More Help

- **Full Guide**: [docs/DESKTOP_APP_INSTALLATION.md](docs/DESKTOP_APP_INSTALLATION.md)
- **Troubleshooting**: See above guide, section "Troubleshooting"
- **Uninstall**: `./scripts/uninstall_desktop_app.sh`

---

**Installed**: ✅
**Location**: Applications Menu → Utilities/Development
**Launch**: Press Super → Type "Llama GPU" → Click
**Quick Access**: Add to Favorites for dock shortcut

**Enjoy your AI assistant!** 🤖✨
