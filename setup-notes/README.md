# Network Kernel Debugging in Proxmox 

## Setting Up Kernel Debugging in Proxmox (fast)

This guide assumes you have already installed the latest version of Windows 11. Detailed installation instructions for Windows 11 are not covered here. Once you have installed Windows 11, clone the VM.

## Configuring the Debugger Machine Host VM Settings 

With two VMs prepared, open the webinterface for proxmox and follow these steps:

1. Navigate through the Proxmox GUI to the CPU settings of the VM.
 
2. In the advanced settings, you will find options to change CPU flags. Make any necessary changes before proceeding, as the menu will become inaccessible afterward (unless you remove the `hv-vendor-id=KVMKVMKVM` from the next steps).

3. Open a root prompt on Proxmox 

Edit the VM configuration file:


```bash
<your-favorite-editor> /etc/pve/nodes/<node-name>/qemu-server/<vm-id>.conf
```
For example, using `vim`:

```bash
vim /etc/pve/nodes/pve-prod/qemu-server/2008.conf
```

Add the following to the CPU variable:


```bash
cpu: <emulated-cpu><,other-variables-for-the-cpu>,hv-vendor-id=KVMKVMKVM
```

In a specific case, it might look like this:


```bash
cpu: kvm,flags=+hv-tblflush;+hv-evmcs;+aes,hv-vendor-id=KVMKVMKVM
```

After this configuration, your VM settings should be correct. However, network settings also need to be configured.

## Setting Up Network 

### Multiple Adapters 

If your VM has multiple network adapters, configure as follows:
 
- Use any adapter type except `e1000` for non-debugging adapters. You will need the `e1000` adapter to interface with the debugger host.

### Single Adapter 

If your VM has a single network adapter, ensure it is set to the `e1000` Intel adapter.


## Follow the rest of the guide on MS

After configuring your VM and network settings, follow the official Microsoft guide to set up network debugging:
[Setting Up a Network Debugging Connection Automatically](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-a-network-debugging-connection-automatically)

## COM Port Debugging 

Add a COM port to both VMs by navigating to the hardware tab, adding a serial port, and selecting a number. This tutorial assumes port 0, but you can change it if needed in the service and in this menu.
After adding a COM port to both VMs, they need to be connected. We use `socat` to create a virtual connection between the serial ports of the two VMs. `socat` is a multipurpose relay tool that allows for bidirectional data transfer between two points. It is chosen for its flexibility and ability to handle different types of connections, including serial ports.To set up `socat`, create a systemd service:

```bash
vim /etc/systemd/system/socat-serial.service
```

Add the following content:


```ini
[Unit]
Description=Socat Serial Connection Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/socat UNIX-CLIENT:/var/run/qemu-server/<id1>.serial0 UNIX-CLIENT:/var/run/qemu-server/<id1>.serial0
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

## Installing socat 
If you do not have `socat` installed, you can install it using `apt`:

```bash
apt update
apt install socat
```

Start the service.

```bash
systemctl start socat-serial
```

Enable the service if you want to use it after proxmox reboot also:

```bash
systemctl enable socat-serial
```