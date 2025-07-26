# Package class for WGUPS Routing Program

class Package:
    def __init__(self, package_id, address, city, zip_code, deadline, weight, note=""):
        self.id = int(package_id)
        self.address = address
        self.city = city
        self.zip = zip_code
        self.deadline = deadline
        self.weight = weight
        self.note = note
        self.status = "At the hub"
        self.delivery_time = None
        self.truck = None

    def __str__(self):
        return (f"Package {self.id}: {self.address}, {self.city} {self.zip}, "
                f"Deadline: {self.deadline}, Weight: {self.weight}kg, "
                f"Status: {self.status} at {self.delivery_time if self.delivery_time else 'N/A'}")
