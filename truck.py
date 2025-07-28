# Truck class and delivery logic for WGUPS

from datetime import timedelta

class Truck:
    def __init__(self, truck_id, departure_time, address_index=0, capacity=16):
        self.id = truck_id
        self.capacity = capacity
        self.packages = []
        self.route = []
        self.mileage = 0.0
        self.speed = 18  # miles per hour
        self.departure_time = departure_time
        self.current_time = departure_time
        self.address_index = address_index  # Hub index
        self.current_location = address_index

    def load_package(self, package):
        if len(self.packages) < self.capacity:
            self.packages.append(package)
            package.truck = self.id
            return True
        return False

    def deliver_packages(self, distance_data, address_lookup):
        # Basic greedy nearest neighbor approach
        unvisited = self.packages[:]
        while unvisited:
            next_package = min(
                unvisited,
                key=lambda p: distance_data[self.current_location][address_lookup[p.address]]
            )
            travel_distance = distance_data[self.current_location][address_lookup[next_package.address]]
            travel_time = timedelta(hours=travel_distance / self.speed)

            self.current_time += travel_time
            self.mileage += travel_distance
            self.current_location = address_lookup[next_package.address]

            next_package.status = "Delivered"
            next_package.delivery_time = self.current_time
            unvisited.remove(next_package)

        # Return to hub
        return_distance = distance_data[self.current_location][0]
        self.mileage += return_distance
        self.current_time += timedelta(hours=return_distance / self.speed)
        self.current_location = 0  # back at hub
