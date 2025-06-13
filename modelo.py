from django.db import models


class ServiceType(models.Model):
    type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.type


class Category(models.Model):
    min_kg = models.BigIntegerField()
    max_kg = models.BigIntegerField()
    usd = models.BigIntegerField()
    cop = models.BigIntegerField()

    def __str__(self):
        return f"{self.min_kg}-{self.max_kg} kg"


class DirectCharge(models.Model):
    unit_of_measure = models.BigIntegerField()
    unit_price_usd = models.BigIntegerField()
    unit_price_cop = models.BigIntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    preparation_time_minutes = models.BigIntegerField()

    def __str__(self):
        return self.description


class Base(models.Model):
    airport = models.ForeignKey('Airport', on_delete=models.CASCADE)
    notes = models.BigIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Base at {self.airport.name}"


class Rates(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.BigIntegerField()
    base = models.ForeignKey(Base, on_delete=models.CASCADE)

    def __str__(self):
        return f"Rate for category {self.category.id}"


class OptTime(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    half_hour_blocks = models.BigIntegerField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class OptValue(models.Model):
    multiplier = models.IntegerField()
    value = models.BigIntegerField()
    created_at = models.BigIntegerField()  # Cambia a DateTimeField si corresponde

    def __str__(self):
        return f"Multiplier: {self.multiplier}, Value: {self.value}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    city = models.BigIntegerField()
    country = models.BigIntegerField()
    icao_code = models.BigIntegerField()
    iata_code = models.BigIntegerField()
    note = models.TextField()
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FlightPlan(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='origin_flights')
    service_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='service_flights')
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='destination_flights')
    estimated_arrival_time = models.DateField()
    estimated_departure_time = models.DateField()
    actual_arrival_time = models.DateField()
    actual_departure_time = models.DateField()
    notes = models.TextField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Flight from {self.origin_airport} to {self.destination_airport}"


class Client(models.Model):
    name = models.CharField(max_length=255)
    is_company = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.BigIntegerField()
    notes = models.TextField()
    created_at = models.DateField()
    tariff = models.ForeignKey(Rates, null=True, blank=True, on_delete=models.SET_NULL)
    tariff_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Aircraft(models.Model):
    registration_code = models.CharField(max_length=50)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)
    aircraft_type = models.BigIntegerField()
    weight = models.BigIntegerField()
    notes = models.BigIntegerField()
    photo = models.BigIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.registration_code


class Service(models.Model):
    name = models.TextField()
    type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    external_service = models.IntegerField(null=True, blank=True)
    id_tf = models.ForeignKey(DirectCharge, null=True, blank=True, on_delete=models.SET_NULL)
    id_dc = models.ForeignKey(Rates, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class OdS(models.Model):
    trip_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    plan = models.ForeignKey(FlightPlan, on_delete=models.CASCADE)
    total = models.IntegerField()
    state_op = models.CharField(max_length=100)
    state_ods = models.CharField(max_length=100)
    state_acm = models.CharField(max_length=100)

    def __str__(self):
        return f"OdS {self.trip_number}"


class ServiceChecklistEntry(models.Model):
    ods = models.ForeignKey(OdS, on_delete=models.CASCADE, related_name='checklist_entries')
    item_name = models.ForeignKey(Service, on_delete=models.CASCADE)
    check = models.BigIntegerField()
    opt_time = models.ForeignKey(OptTime, null=True, blank=True, on_delete=models.SET_NULL)
    opt_value = models.ForeignKey(OptValue, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item_name.name} for ODS {self.ods.trip_number}"


class Receipt(models.Model):
    ods = models.ForeignKey(OdS, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    issued_date = models.BigIntegerField()  # Considera usar DateField o DateTimeField
    base = models.ForeignKey(Base, on_delete=models.CASCADE)
    services = models.BigIntegerField()
    total_amount = models.BigIntegerField()
    currency = models.BigIntegerField()
    status = models.BigIntegerField()
    created_at = models.BigIntegerField()
    updated_at = models.BigIntegerField(null=True, blank=True)
    was_modified = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Receipt for {self.ods.trip_number}"
