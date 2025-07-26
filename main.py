# Student ID: 012096094

import csv
from datetime import datetime, timedelta
from utils import str_to_time, time_to_str, format_package_status

# Constants
MAX_PACKAGES_PER_TRUCK = 16
TRUCK_SPEED_MPH = 18
START_TIME = datetime.strptime("08:00", "%H:%M").time()
PACKAGE_9_CORRECTION_TIME = datetime.strptime("10:20", "%H:%M").time()
PACKAGE_9_CORRECTED_ADDRESS = "410 S State St"

# --- HASH TABLE IMPLEMENTATION ---

class PackageHashTable:
    def __init__(self, size=40):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, package_id):
        return package_id % self.size

    def insert(self, package_id, address, deadline, city, zip_code, weight, note=""):
        index = self._hash(package_id)
        # Initialize package data dictionary
        package_data = {
            'id': package_id,
            'address': address,
            'deadline': deadline,
            'city': city,
            'zip_code': zip_code,
            'weight': weight,
            'note': note,
            'status': 'At Hub',
            'delivery_time': None,
            'truck': None,
            'original_address': address,  # Store original address for package 9
            'available_time': None,  # For delayed packages
            'group_with': []  # For packages that must be delivered together
        }
        
        # Handle special cases
        if package_id == 9:
            package_data['status'] = 'Wrong Address - Cannot Deliver'
        
        # Handle flight delays
        if "Delayed on flight" in note:
            package_data['available_time'] = datetime.strptime("09:05", "%H:%M").time()
            package_data['status'] = 'Delayed - Not Available'
        
        # Handle package grouping
        if "Must be delivered with" in note:
            # Extract package IDs from note - handle quoted format from CSV
            import re
            # Look for numbers after "with" in the note
            match = re.search(r'with (\d+), (\d+)', note)
            if match:
                numbers = [int(match.group(1)), int(match.group(2))]
                package_data['group_with'] = numbers
            else:
                # Fallback: extract all numbers and skip the first (current package ID)
                numbers = re.findall(r'\d+', note)
                if len(numbers) >= 3:  # Current package + 2 others
                    package_data['group_with'] = [int(num) for num in numbers[1:3]]  # Skip first, take next 2
        
        # Insert or update package
        for idx, item in enumerate(self.table[index]):
            if item['id'] == package_id:
                self.table[index][idx] = package_data
                return
        self.table[index].append(package_data)

    def lookup(self, package_id):
        index = self._hash(package_id)
        for item in self.table[index]:
            if item['id'] == package_id:
                return item
        return None

    def update_status(self, package_id, status, delivery_time=None, truck=None):
        package = self.lookup(package_id)
        if package:
            package['status'] = status
            package['delivery_time'] = delivery_time
            if truck:
                package['truck'] = truck

    def update_address(self, package_id, new_address):
        package = self.lookup(package_id)
        if package:
            package['address'] = new_address
            if package['status'] == 'Wrong Address - Cannot Deliver':
                package['status'] = 'At Hub'

    def all_packages(self):
        packages = []
        for bucket in self.table:
            packages.extend(bucket)
        return packages

    def get_available_packages_at_time(self, query_time):
        """Get packages available for delivery at a specific time"""
        available = []
        for package in self.all_packages():
            # Check if package is available (not delayed or wrong address)
            if package['available_time'] and query_time < package['available_time']:
                continue
            if package['status'] == 'Wrong Address - Cannot Deliver':
                continue
            available.append(package)
        return available

    def reset_delivery_state(self):
        """Reset all packages to their initial delivery state"""
        for package in self.all_packages():
            package['status'] = 'At Hub'
            package['delivery_time'] = None
            # Reset package 9 to wrong address status
            if package['id'] == 9:
                package['status'] = 'Wrong Address - Cannot Deliver'
                package['address'] = package['original_address']
            # Reset delayed packages
            if "Delayed on flight" in package['note']:
                package['status'] = 'Delayed - Not Available'

# --- TRUCK CLASS ---

class Truck:
    def __init__(self, truck_id):
        self.truck_id = truck_id
        self.packages = []
        self.miles_traveled = 0.0
        self.current_time = START_TIME
        self.current_location = 'Hub'
        self.route = []

    def load_package(self, package_id):
        if len(self.packages) < MAX_PACKAGES_PER_TRUCK:
            self.packages.append(package_id)
            return True
        return False

    def deliver_package(self, package_id, delivery_time):
        if package_id in self.packages:
            self.packages.remove(package_id)
            return True
        return False

    def can_load_package(self, package, package_table):
        """Check if truck can load a specific package based on constraints"""
        # Check truck-specific constraints
        if "Can only be on truck 2" in package['note'] and self.truck_id != 2:
            return False
        
        # Check capacity
        if len(self.packages) >= MAX_PACKAGES_PER_TRUCK:
            return False
            
        return True

    def reset_state(self):
        """Reset truck to initial state"""
        self.miles_traveled = 0.0
        self.current_time = START_TIME
        self.current_location = 'Hub'

# --- MAIN DELIVERY PROGRAM ---

def load_packages(filename, package_table):
    """Load packages from CSV into the hash table"""
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            package_id = int(row[0])
            address = row[1]
            city = row[2]
            deadline = row[5]
            zip_code = row[4]
            weight = row[6]
            note = row[7] if len(row) > 7 else ""
            package_table.insert(package_id, address, deadline, city, zip_code, weight, note)

def assign_packages_to_trucks(package_table, trucks):
    """Assign packages to trucks based on constraints and requirements, with correct grouping."""
    all_packages = package_table.all_packages()
    # 1. Build grouping graph
    from collections import defaultdict, deque
    graph = defaultdict(set)
    id_to_package = {pkg['id']: pkg for pkg in all_packages}
    for pkg in all_packages:
        for other_id in pkg.get('group_with', []):
            graph[pkg['id']].add(other_id)
            graph[other_id].add(pkg['id'])
    # 2. Find all connected groups (connected components)
    visited = set()
    groups = []
    for pkg in all_packages:
        if pkg['id'] not in visited and pkg['group_with']:
            # BFS to find all connected packages
            group = set()
            queue = deque([pkg['id']])
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    group.add(current)
                    for neighbor in graph[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)
            if group:
                groups.append([id_to_package[pid] for pid in group])
    # 3. Assign each group to a truck as a unit (excluding delayed packages)
    for group in groups:
        # Filter out delayed packages from initial assignment
        available_group = [pkg for pkg in group if not pkg.get('available_time')]
        if available_group:
            assigned = False
            for truck in trucks:
                if all(truck.can_load_package(pkg, package_table) for pkg in available_group):
                    for pkg in available_group:
                        if truck.load_package(pkg['id']):
                            package_table.update_status(pkg['id'], 'Assigned to Truck', truck=truck.truck_id)
                    assigned = True
                    break
            if not assigned:
                print(f"Warning: Could not assign grouped packages {[pkg['id'] for pkg in available_group]} to any truck")
    # 4. Assign truck-specific packages first (packages that can only be on truck 2, excluding delayed)
    truck2_only_packages = [pkg for pkg in all_packages if pkg['truck'] is None and "Can only be on truck 2" in pkg['note'] and not pkg.get('available_time')]
    for package in truck2_only_packages:
        truck2 = next((truck for truck in trucks if truck.truck_id == 2), None)
        if truck2 and truck2.can_load_package(package, package_table):
            if truck2.load_package(package['id']):
                package_table.update_status(package['id'], 'Assigned to Truck', truck=truck2.truck_id)
        else:
            print(f"Warning: Could not assign package {package['id']} to truck 2")
    # 5. Assign remaining packages (excluding those already assigned in groups or truck-specific, and delayed)
    for package in all_packages:
        if package['truck'] is None and not package.get('available_time'):  # Not yet assigned and not delayed
            assigned = False
            for truck in trucks:
                if truck.can_load_package(package, package_table):
                    if truck.load_package(package['id']):
                        package_table.update_status(package['id'], 'Assigned to Truck', truck=truck.truck_id)
                        assigned = True
                        break
            if not assigned:
                print(f"Warning: Could not assign package {package['id']} to any truck")
    # 6. Assign delayed packages to trucks (they'll be loaded after 9:05 AM)
    delayed_packages = [pkg for pkg in all_packages if pkg.get('available_time')]
    for package in delayed_packages:
        if package['truck'] is None:  # Not yet assigned
            assigned = False
            for truck in trucks:
                if truck.can_load_package(package, package_table):
                    if truck.load_package(package['id']):
                        package_table.update_status(package['id'], 'Assigned to Truck', truck=truck.truck_id)
                        assigned = True
                        break
            if not assigned:
                print(f"Warning: Could not assign delayed package {package['id']} to any truck")

def simulate_delivery(package_table, trucks, query_time):
    """Simulate delivery process up to the query time"""
    # Reset all state first
    package_table.reset_delivery_state()
    for truck in trucks:
        truck.reset_state()
    
    # Update package 9 address if past correction time
    if query_time >= PACKAGE_9_CORRECTION_TIME:
        package_table.update_address(9, PACKAGE_9_CORRECTED_ADDRESS)
    
    # Create a timeline of all delivery events
    delivery_events = []
    
    # Simulate delivery for each truck (8:00 AM departure)
    for truck in trucks:
        truck.current_time = START_TIME
        # Only load packages that are available at departure time (8:00 AM)
        # Delayed packages are NOT loaded at 8:00 AM
        available_packages = []
        for pkg_id in truck.packages:
            package = package_table.lookup(pkg_id)
            # Skip packages with wrong address
            if package['status'] == 'Wrong Address - Cannot Deliver':
                continue
            # Skip delayed packages - they are NOT loaded at 8:00 AM
            if package.get('available_time'):
                continue
            available_packages.append(pkg_id)
        
        # Process deliveries in time order
        current_time = truck.current_time
        for pkg_id in available_packages:
            package = package_table.lookup(pkg_id)
            
            # Calculate delivery time (simplified - each delivery takes 15 minutes)
            delivery_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=15)).time()
            
            # Add to delivery events
            delivery_events.append({
                'package_id': pkg_id,
                'truck_id': truck.truck_id,
                'delivery_time': delivery_time,
                'miles': 3.0
            })
            
            current_time = delivery_time
    
    # Now handle delayed packages that arrive at depot at 9:05 AM
    # These packages are loaded and delivered after they arrive
    delayed_packages = []
    for truck in trucks:
        for pkg_id in truck.packages:
            package = package_table.lookup(pkg_id)
            if package.get('available_time') == datetime.strptime("09:05", "%H:%M").time():
                delayed_packages.append((pkg_id, truck.truck_id))
    
    # Add delayed package deliveries starting at 9:05 AM
    delayed_start_time = datetime.strptime("09:05", "%H:%M").time()
    current_delayed_time = delayed_start_time
    for pkg_id, truck_id in delayed_packages:
        # Add loading time (instantaneous as per requirements)
        delivery_time = (datetime.combine(datetime.today(), current_delayed_time) + timedelta(minutes=15)).time()
        delivery_events.append({
            'package_id': pkg_id,
            'truck_id': truck_id,
            'delivery_time': delivery_time,
            'miles': 3.0
        })
        current_delayed_time = delivery_time
    
    # Sort delivery events by time
    delivery_events.sort(key=lambda x: x['delivery_time'])
    
    # Apply delivery events up to query time
    for event in delivery_events:
        if event['delivery_time'] <= query_time:
            package_table.update_status(event['package_id'], 'Delivered', event['delivery_time'], event['truck_id'])
            # Update truck mileage
            for truck in trucks:
                if truck.truck_id == event['truck_id']:
                    truck.miles_traveled += event['miles']
                    break
        else:
            # Package is en route at query time
            package_table.update_status(event['package_id'], 'En Route', None, event['truck_id'])

def print_package_status_at_time(package_table, query_time, trucks=None):
    """Display status of all packages at a specific time with all required fields"""
    print(f"\n{'='*100}")
    print(f"PACKAGE STATUS AT {time_to_str(query_time)}")
    print(f"{'='*100}")
    
    # Simulate delivery up to query time
    if trucks:
        simulate_delivery(package_table, trucks, query_time)
    
    # Get all packages and sort by ID
    all_packages = package_table.all_packages()
    all_packages.sort(key=lambda pkg: int(pkg['id']))
    
    print(f"{'ID':<3} {'Address':<20} {'City':<12} {'Zip':<6} {'Deadline':<8} {'Truck':<5} {'Status':<18} {'Weight':<5} {'Delivery':<10}")
    print("-" * 100)
    
    for pkg in all_packages:
        # Determine address to display
        if pkg['id'] == 9 and query_time < PACKAGE_9_CORRECTION_TIME:
            display_address = pkg['original_address'] + " (WRONG)"
        else:
            display_address = pkg['address']
        
        # Determine status
        if pkg['status'] == 'Delivered' and pkg['delivery_time'] and pkg['delivery_time'] <= query_time:
            status = f"Delivered at {time_to_str(pkg['delivery_time'])}"
        elif pkg['status'] == 'Wrong Address - Cannot Deliver':
            status = "Wrong Address - Cannot Deliver"
        elif pkg.get('available_time') and query_time < pkg['available_time']:
            # Package is delayed and not yet available
            status = f"Delayed on flight until {time_to_str(pkg['available_time'])}"
        elif pkg['status'] == 'En Route':
            status = "En Route"
        else:
            status = "At Hub"
        
        # Format delivery time
        delivery_time_str = time_to_str(pkg['delivery_time']) if pkg['delivery_time'] else "N/A"
        
        # Format truck number
        truck_str = str(pkg['truck']) if pkg['truck'] else "N/A"
        
        print(f"{pkg['id']:<3} {display_address:<20} {pkg['city']:<12} {pkg['zip_code']:<6} {pkg['deadline']:<8} {truck_str:<5} {status:<18} {pkg['weight']:<5} {delivery_time_str:<10}")
    
    # Display truck mileage
    if trucks:
        print(f"\n{'='*50}")
        print("TRUCK MILEAGE")
        print(f"{'='*50}")
        total_miles = 0
        for truck in trucks:
            print(f"Truck {truck.truck_id}: {truck.miles_traveled:.2f} miles")
            total_miles += truck.miles_traveled
        print(f"Total mileage: {total_miles:.2f} miles")

def print_single_package_status_at_time(package_table, package_id, query_time, trucks=None):
    """Display status of a specific package at a given time"""
    pkg = package_table.lookup(package_id)
    if not pkg:
        print(f"No package found with ID {package_id}.")
        return
    
    # Simulate delivery up to query time
    if trucks:
        simulate_delivery(package_table, trucks, query_time)
        pkg = package_table.lookup(package_id)  # Refresh package data
    
    print(f"\n{'='*60}")
    print(f"PACKAGE {package_id} STATUS AT {time_to_str(query_time)}")
    print(f"{'='*60}")
    
    # Determine address to display
    if pkg['id'] == 9 and query_time < PACKAGE_9_CORRECTION_TIME:
        display_address = pkg['original_address'] + " (WRONG ADDRESS)"
    else:
        display_address = pkg['address']
    
    # Determine status
    if pkg['status'] == 'Delivered' and pkg['delivery_time'] and pkg['delivery_time'] <= query_time:
        status = f"Delivered at {time_to_str(pkg['delivery_time'])}"
    elif pkg['status'] == 'Wrong Address - Cannot Deliver':
        status = "Wrong Address - Cannot Deliver"
    elif pkg.get('available_time') and query_time < pkg['available_time']:
        # Package is delayed and not yet available
        status = f"Delayed on flight until {time_to_str(pkg['available_time'])}"
    elif pkg['status'] == 'En Route':
        status = "En Route"
    else:
        status = "At Hub"
    
    print(f"Package ID: {pkg['id']}")
    print(f"Address: {display_address}")
    print(f"City: {pkg['city']}")
    print(f"Zip Code: {pkg['zip_code']}")
    print(f"Deadline: {pkg['deadline']}")
    print(f"Weight: {pkg['weight']}")
    print(f"Truck: {pkg['truck'] if pkg['truck'] else 'Not Assigned'}")
    print(f"Status: {status}")
    if pkg['delivery_time']:
        print(f"Delivery Time: {time_to_str(pkg['delivery_time'])}")
    if pkg['note']:
        print(f"Special Notes: {pkg['note']}")

def main():
    # Create package hash table
    package_table = PackageHashTable()

    # Load packages from CSV file
    load_packages("csv/packages.csv", package_table)

    # Initialize trucks
    trucks = [Truck(1), Truck(2), Truck(3)]

    # Assign packages to trucks
    assign_packages_to_trucks(package_table, trucks)

    # User interface loop
    print("WGUPS Delivery System")
    print("Available commands:")
    print("  [time]                - View all package statuses at that time (e.g., '9:15 AM')")
    print("  [time] [package_id]    - View a specific package's status at that time (e.g., '9:15 AM 12')")
    print("  mileage                - View total mileage traveled by all trucks")
    print("  exit                   - Quit the program")
    
    while True:
        print("\n" + "="*50)
        print("Available commands:")
        print("  [time]                - View all package statuses at that time (e.g., '9:15 AM')")
        print("  [time] [package_id]    - View a specific package's status at that time (e.g., '9:15 AM 12')")
        print("  mileage                - View total mileage traveled by all trucks")
        print("  exit                   - Quit the program")
        print("="*50)
        
        user_input = input("Enter command: ").strip()
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'mileage':
            # Run full simulation to get accurate mileage
            end_of_day = datetime.strptime("23:59", "%H:%M").time()
            simulate_delivery(package_table, trucks, end_of_day)
            total_miles = sum(truck.miles_traveled for truck in trucks)
            print(f"\nTotal mileage traveled by all trucks: {total_miles:.2f} miles")
            continue
        
        # Parse input for time and optional package ID
        parts = user_input.split()
        
        if len(parts) >= 3:
            # Assume last part is package ID, rest is time
            try:
                package_id = int(parts[-1])
                time_str = ' '.join(parts[:-1])
                query_time = datetime.strptime(time_str, "%I:%M %p").time()
                print_single_package_status_at_time(package_table, package_id, query_time, trucks)
            except ValueError:
                print("Invalid input. Please enter time as HH:MM AM/PM and a valid package ID (e.g., '9:15 AM 12').")
            continue
        elif len(parts) >= 2:
            # Try to parse as time and package ID
            try:
                package_id = int(parts[-1])
                time_str = ' '.join(parts[:-1])
                query_time = datetime.strptime(time_str, "%I:%M %p").time()
                print_single_package_status_at_time(package_table, package_id, query_time, trucks)
            except ValueError:
                # Try as just time for all packages
                try:
                    query_time = datetime.strptime(user_input, "%I:%M %p").time()
                    print_package_status_at_time(package_table, query_time, trucks)
                except ValueError:
                    print("Invalid time format. Please enter time as HH:MM AM/PM (e.g., 9:15 AM) or '9:15 AM 12' for a specific package.")
            continue
        else:
            # Try as just time for all packages
            try:
                query_time = datetime.strptime(user_input, "%I:%M %p").time()
                print_package_status_at_time(package_table, query_time, trucks)
            except ValueError:
                print("Invalid input. Please enter a valid command, time, or 'exit'.")
    
    # Print total mileage on exit
    total_miles = sum(truck.miles_traveled for truck in trucks)
    print(f"\nTotal mileage traveled by all trucks: {total_miles:.2f} miles")

if __name__ == "__main__":
    main()
