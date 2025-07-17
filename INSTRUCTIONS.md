# Instructions for running on a Home Assistant NUC

This guide assumes you have a basic understanding of the command line and have SSH access to your Home Assistant NUC.

## 1. Copy the add-on files

First, you need to copy the `smarthq_addon` directory to the `/config/custom_components` directory on your Home Assistant NUC. You can do this using `scp` or by setting up a Samba share.

**Using `scp`:**

```bash
scp -r smarthq_addon/ user@your_home_assistant_ip:/config/custom_components/
```

Replace `user` with your SSH username and `your_home_assistant_ip` with the IP address of your Home Assistant NUC.

## 2. Install the dependencies

Next, you need to install the Python dependencies listed in `requirements.txt`. SSH into your Home Assistant NUC and run the following commands:

```bash
pip install -r /config/custom_components/smarthq_addon/requirements.txt
```

## 3. Configure the add-on

You will need to edit the `config.yaml` file to match your SmartHQ credentials.

```bash
nano /config/custom_components/smarthq_addon/config.yaml
```

## 4. Restart Home Assistant

Finally, restart Home Assistant for the changes to take effect. You can do this from the Home Assistant UI by going to **Configuration** > **Server Controls** and clicking **Restart**.

After Home Assistant restarts, the SmartHQ integration should be available to add from the **Integrations** page.
