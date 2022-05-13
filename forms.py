from flask_wtf import FlaskForm
from wtforms import validators, BooleanField, StringField, PasswordField, SubmitField, SelectField, DecimalField, DateField, IntegerField, SelectMultipleField, FormField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms_components import DateRange
from database import Database as db
from datetime import datetime, date

states_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
          'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
          'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
          'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
          'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI',
          'WY', 'AS', 'GU', 'MH', 'FM', 'MP', 'PW', 'PR', 'VI']
customer_type_list = ['Individual', 'Business']
color_list = ['Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze',
              'Claret', 'Copper', 'Cream', 'Gold', 'Gray', 'Green',
              'Maroon', 'Metallic', 'Navy', 'Orange', 'Pink', 'Purple',
              'Red', 'Rose', 'Rust', 'Silver', 'Tan', 'Turquoise', 'White', 'Yellow']
manufacturer_name = ['Acura', 'Alfa Romeo', 'Aston Martin', 'Audi', 'Bentley',
                     'BMW', 'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge',
                     'Ferrari', 'FIAT', 'Ford', 'Freightliner', 'Genesis', 'GMC',
                     'Honda', 'Hyundai', 'INFINITI', 'Jaguar', 'Jeep', 'Kia', 'Lamborghini',
                     'Land Rover', 'Lexus', 'Lincoln', 'Lotus', 'Maserati', 'MAZDA',
                     'McLaren', 'Mercedes-Benz', 'MINI', 'Mitsubishi', 'Nissan', 'Porsche',
                     'Ram', 'Rolls-Royce', 'smart', 'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo']
vehicle_type = ["Sedan", "Coupe", "Convertible", "Truck", "Van", "Minivan", "SUV", "Other"]
vehicle_status = ['Excellent', 'Very Good', 'Good', 'Fair']
repair_status = ['pending', 'in progress', 'completed']


class AddRecallForm(FlaskForm):
    nhtsa = StringField('NHTSA', [DataRequired(), validators.Length(max=250)])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[(i, i) for i in manufacturer_name],
        validators=[DataRequired(), validators.Length(max=250)])
    description = StringField('Description', [validators.Length(max=250)])
    add_recall_button = SubmitField('Add Recall')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SearchVehicleForm(FlaskForm):
    current_year = int(datetime.now().year)
    vin = StringField('VIN', [validators.Length(max=17, message="Not a valid VIN")])
    vehicle_type_result, manufacturer_result = [], []
    try:
        vehicle_type_result = db.get_vehicle_type()
    except:
        vehicle_type_result = vehicle_type
    try:
        manufacturer_result = db.get_manufacturer()
    except:
        manufacturer_result = manufacturer_name
    model_year = SelectField(
        label='Model Year', 
        choices=[('', 'Any')] + [(str(i), str(i)) for i in range(1800, current_year + 2)])
    vehicle_type_name = SelectField(
        label='Vehicle Type', 
        choices=[('', 'Any')] + [(i, i) for i in vehicle_type_result])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[('', 'Any')] + [(i, i) for i in manufacturer_result])
    colors = SelectField('Color', choices=[('', 'Any')] + [(i, i) for i in color_list])
    keyword = StringField('Keyword', [validators.Length(max=250)])
    sortby = SelectField(
        label='Sort By',
        choices=[('vehicle_vin', 'VIN'), 
                 ('vehicle_type_name', 'Vehicle Type'), 
                 ('model_year', 'Model Year'),
                 ('manufacturer_name', 'Manufacturer'),
                 ('model_name', 'Model'),
                 ('mileage', 'Mileage'),
                 ('cost_price', 'Price')],
        validators=[DataRequired()])
    filterby = SelectField(
        label='Filter by',
        choices=[],
        validators=[DataRequired()])
    submit_button = SubmitField('Search Vehicle')

class AddVehicleForm(FlaskForm):
    vin = StringField('VIN', [DataRequired(), validators.Length(min=11, max=17, message="Invalid VIN (min length = 11, max length = 17)")])
    model_name = StringField('Model Name', [DataRequired(), validators.Length(max=250)])
    model_year = DateField('Model Year',
        default=date.today(),
        format="%Y",
        validators=[DataRequired(),
        DateRange(message="Year must be less than " + str(date.today().year+2),
                  max=date(date.today().year+2, 1, 1))])
    cost_price = DecimalField(
        label='Cost Price',
        places=2,
        validators=[DataRequired(), NumberRange(min=0)])
    invent_start_dt = DateField(
        'Start Date',
        default=date.today(),
        format="%Y-%m-%d",
        validators=[DataRequired(), DateRange(message="Future date is not allowed", max=date.today())])
    car_condition = SelectField(
        label='Condition',
        choices=[(i, i) for i in vehicle_status],
        validators=[DataRequired()])
    mileage = IntegerField(
        'Mileage',
        validators=[DataRequired("Invalid entry. Please enter an positive integer."), NumberRange(min=0)])
    description = StringField('Description', validators=[validators.Length(max=250)])
    vehicle_type_name = SelectField(
        label='Vehicle Type',
        choices=[(i, i) for i in vehicle_type],
        validators=[DataRequired()])
    manufacturer = SelectField(
        label='Manufacturer',
        choices=[(i, i) for i in manufacturer_name],
        validators=[DataRequired()])
    colors = SelectMultipleField(
        label='Color(s)',
        id='color_list',
        choices=[(i, i) for i in color_list],
        validators=[]
    )
    add_vehicle_button = SubmitField('Add Vehicle')

class AddManufacturer(FlaskForm):
    manufacturer = StringField('Manufacturer Name', [DataRequired(), validators.Length(max=250)])
    add_manufacturer_button = SubmitField('Add Manufacturer')

class AddVehicleType(FlaskForm):
    vehicle_type = StringField('Vehicle Type', [DataRequired(), validators.Length(max=250)])
    add_vehicle_type_button = SubmitField('Add Vehicle Type')

class AddCustomerForm(FlaskForm):
    email = StringField('Email', [validators.Length(max=250), validators.Email(message=('Invalid email address.'))])
    phone_num = StringField('Phone', [DataRequired(), validators.Length(max=32)])
    street = StringField('Street', [DataRequired(), validators.Length(max=250)])
    city = StringField('City', [DataRequired(), validators.Length(max=250)])
    state = SelectField(
        label='State',
        choices=[(i, i) for i in states_list],
        validators=[DataRequired()])
    zip_code = StringField('Zip Code', [DataRequired(), validators.Length(max=60)])

class AddIndividualForm(FlaskForm):
    driver_license_num = StringField("Driver's License Number", [DataRequired(), validators.Length(max=100)])
    first_name = StringField('First Name', [DataRequired(), validators.Length(max=100)])
    last_name = StringField('Last Name', [DataRequired(), validators.Length(max=100)])
    customer_form = FormField(AddCustomerForm, label='')
    add_individual_customer_button = SubmitField('Add Individual Customer')

class AddBusinessForm(FlaskForm):
    tin = StringField('Tax Identification Number', [DataRequired(), validators.Length(max=100)])
    company_name = StringField('Company Name', [DataRequired(), validators.Length(max=250)])
    primary_contact = StringField('Primary Contact', [DataRequired(), validators.Length(max=250)])
    primary_contact_title = StringField('Primary Contact Title', [DataRequired(), validators.Length(max=100)])
    customer_form = FormField(AddCustomerForm, label='')
    add_business_customer_button = SubmitField('Add Business Customer')

class SearchCustomerForm(FlaskForm):
    customer_type = SelectField(
        label='Customer Type',
        id='customer_type',
        choices=[(i, i) for i in customer_type_list],
        validators=[DataRequired()])
    identification_num = StringField(
        label='Identification Number',
        description="* For Individual, please enter driver's license. For Business, please enter tax identification number.", 
        validators=[DataRequired(), validators.Length(max=100)])
    search_customer_button = SubmitField('Search Customer')

class RecordSalesForm(FlaskForm):
    sales_date = DateField('Sales Date',
                           default=date.today(),
                           format='%Y-%m-%d',
                           id='sales_date',
                           validators=[DataRequired("Follow the format: YYYY-MM-DD"),
                                       DateRange(message="Future date is not allowed", max=date.today())])
    record_sales_button = SubmitField('Record Sales')

class AddRepairForm(FlaskForm):
    vin = StringField('Enter VIN number', [validators.Length(max=250)])
    start_date = DateField('Start Date', format="%m/%d/%Y")
    end_date =  DateField('End Date', format="%m/%d/%Y")
    description = StringField('Description', [validators.Length(max=250)])
    cost = IntegerField('Cost')
    vendor_name = SelectField(
        label='Vendor Name')
    submit_button = SubmitField('Add Repair')

