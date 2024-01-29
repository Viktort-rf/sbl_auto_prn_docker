from flask import Flask, render_template, redirect, url_for, request
import winrm
import re
import os

app = Flask(__name__)


# Get variable from .env
dhcp_ip = os.environ.get("DHCP_IP")
winrm_username = os.environ.get(r"WINRM_USERNAME")
winrm_password = os.environ.get("WINRM_PASSWORD")
winrm_port = os.environ.get("WINRM_PORT")
allow_prn_manufacturer_str = os.environ.get("PRN_MANUFACTURER", "")
prn_manufacturer = allow_prn_manufacturer_str.split(",")
print("winrm_username:", winrm_username)
print("winrm_password:", winrm_password)
print("winrm_port:", winrm_port)
print("dhcp_ip:", dhcp_ip)
print("prn_manufacturer:", prn_manufacturer)


def add_dhcp_binding_and_log(dhcp_ip, client_mac, winrm_username, winrm_password, winrm_port):

    powershell_script = f"Get-DhcpServerv4Scope | Get-DhcpServerv4Lease -EA SilentlyContinue -ClientId {client_mac} | Add-DhcpServerv4Reservation -Type Dhcp -Description auto_add_by_web"
    winrm_host = f"http://{dhcp_ip}:{winrm_port}/wsman"

    try:
        session = winrm.Session(
            winrm_host,
            auth=(winrm_username, winrm_password),
            server_cert_validation="ignore",
            transport="ntlm"
        )

        result = session.run_ps(powershell_script)

        # TEMP. Save MAC in local file
        with open("data.txt", "a") as file:
            file.write(client_mac + "\n")

    except Exception as e:
        return None, f"ERROR: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    dhcp_ip = os.environ.get("DHCP_IP")
    winrm_username = os.environ.get(r"WINRM_USERNAME")
    winrm_password = os.environ.get("WINRM_PASSWORD")
    winrm_port = os.environ.get("WINRM_PORT")
    allow_prn_manufacturer_str = os.environ.get("PRN_MANUFACTURER", "")
    prn_manufacturer = allow_prn_manufacturer_str.split(",")
    print("winrm_username:", winrm_username)
    print("winrm_password:", winrm_password)
    print("winrm_port:", winrm_port)
    print("dhcp_ip:", dhcp_ip)
    print("prn_manufacturer:", prn_manufacturer)

    success_message = None
    error_message = None

    if request.method == "POST":

        # Get mac-addr printer from user
        client_mac = request.form["user_input"]
        regex_pattern = re.compile("^[a-z0-9]+$")


        # Check input mac-addr is correct format
        if not regex_pattern.match(client_mac):
            error_message = "ERROR: МАС-ADDR must contain only lowercase latin letters and numbers."
            return render_template("index.html", error_message=error_message)


        # Check input mac-addr is printer manufacturer
        if client_mac.startswith(tuple(prn_manufacturer)):

            # Execute function
            error = add_dhcp_binding_and_log(dhcp_ip, client_mac, winrm_username, winrm_password, winrm_port)
            if error:
                error_message = "ERROR: " + str(error)
            else:
                success_message = "SUCCESS"
                return redirect(url_for("success"))

        else:
            error_message = "ERROR: MAC-ADDR not printer. Check it and try again"

    return render_template("index.html", success_message=success_message, error_message=error_message)

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
