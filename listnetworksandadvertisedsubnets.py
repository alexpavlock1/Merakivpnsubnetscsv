import asyncio
import meraki.aio
import csv

API_KEY = ''
ORG_ID = ''  # Replace with your actual organization ID

def print_colored(message, color):
    colors = {
        'green': '\033[92m',  # Green text
        'red': '\033[91m',    # Red text
        'purple': '\033[95m', # Purple text
    }
    reset_code = '\033[0m'  # Reset to default text color
    print(f"{colors.get(color, '')}{message}{reset_code}")

async def main():
    async with meraki.aio.AsyncDashboardAPI(api_key=API_KEY) as dashboard:
        try:
            # Get the organization's networks
            networkresponse = await dashboard.organizations.getOrganizationNetworks(ORG_ID)

            # Prepare CSV file
            with open(f'networks_vpn_subnets_OrgID_{ORG_ID}.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Network Name', 'Network ID', 'Subnet'])

                for network in networkresponse:
                    network_id = network['id']
                    network_name = network['name']
                    product_types = network.get('productTypes', [])

                    # Check if the network has a security appliance
                    if 'appliance' in product_types:
                        try:
                            # Get the VPN settings for each network
                            vpn_settings = await dashboard.appliance.getNetworkApplianceVpnSiteToSiteVpn(network_id)

                            first_subnet = True
                            for subnet in vpn_settings.get('subnets', []):
                                if subnet['useVpn']:
                                    local_subnet = subnet['localSubnet']
                                    
                                    if first_subnet:
                                        writer.writerow([network_name, network_id, local_subnet])
                                        first_subnet = False
                                    else:
                                        writer.writerow(['', '', local_subnet])

                        except meraki.aio.AsyncAPIError as e:
                            print_colored(f"API Error for network {network_name} ({network_id}): {e}", 'red')

        except meraki.aio.AsyncAPIError as e:
            print_colored(f"API Error: {e}", 'red')

if __name__ == '__main__':
    asyncio.run(main())
