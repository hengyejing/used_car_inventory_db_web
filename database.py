import pymysql

host = "omscs2019team20.mysql.database.azure.com"
user = "dbadmin@omscs2019team20"
password = "DBsummer2019"
db = "usedcar"

class Database:
    conn = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)

    ## test sample: list customers
    @classmethod
    def list_customers(cls):
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute("SELECT customerID, email, phone_num FROM Customer LIMIT 50")
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

    @classmethod
    def getUser(cls,username, password):
        query = "SELECT CONCAT(i.first_name, ' ', i.last_name) as firstname, s.username as saleperson, ic.username as clerk, m.username as manager FROM internaluser i\
                left join salesperson s on i.username = s.username\
                left join inventoryclerk ic on i.username = ic.username\
                left join manager m on i.username = m.username\
                where i.username=%s and i.password = %s"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query,(username,password))
                result = cur.fetchone()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

    @classmethod
    def get_inventory_clerk(cls):
        query = "SELECT username FROM InventoryClerk"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return [i['username'] for i in result]
        except Exception as e:
            print (e)
        finally:
            print (query)

    @classmethod
    def get_manufacturer(cls):
        query = "SELECT manufacturer_name FROM Manufacturer"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return [i['manufacturer_name'] for i in result]
        except Exception as e:
            print (e)
        finally:
            print (query)

    @classmethod
    def add_manufacturer(cls, manufacturer):
        query = "INSERT INTO Manufacturer(manufacturer_name) VALUES (%s);"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (manufacturer))
                cls.conn.commit()
            return "Add manufacturer '{}'' successful".format(manufacturer)
        except Exception as e:
            print (e)
            if e.args[0] == 1062:
                return "Duplicate entry '{}'".format(manufacturer)
            else:
                return str(e)
        finally:
            print (query)

    @classmethod
    def get_vehicle_type(cls):
        query = "SELECT vehicle_type_name FROM VehicleType"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return [i['vehicle_type_name'] for i in result]
        except Exception as e:
            print (e)

        finally:
            print (query)

    @classmethod
    def get_vendors(cls):
        query = "SELECT vendor_name FROM vendor"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return [i['vendor_name'] for i in result]
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

    @classmethod
    def add_vehicle_type(cls, vehicle_type):
        query = "INSERT INTO VehicleType(vehicle_type_name) VALUES (%s);"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (vehicle_type))
                cls.conn.commit()
            return "Add vehicle type '{} successful".format(vehicle_type)
        except Exception as e:
            print (e)
            if e.args[0] == 1062:
                return "Duplicate entry '{}'".format(vehicle_type)
            else:
                return str(e)
        finally:
            print (query)

    @classmethod
    def get_recalls(cls):
        query = "SELECT NHTSA_number FROM Recall"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            return [i['NHTSA_number'] for i in result]
        except Exception as e:
            print (e)
        finally:
            print (query)

    @classmethod
    def get_recall(cls, nhtsa):
        query = "SELECT NHTSA_number FROM Recall WHERE NHTSA_number=%s"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (nhtsa))
                result = cur.fetchone()
            return result
        except Exception as e:
            print (e)
        finally:
            print (query)

    @classmethod
    def add_recall(cls, nhtsa, manufacturer, description):
        query = "INSERT INTO Recall (NHTSA_number, manufacturer_name, description) \
                 VALUES (%s, %s, %s);"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (nhtsa, manufacturer, description))
                cls.conn.commit()
            return "Add recall '{}' successful".format(nhtsa)
        except Exception as e:
            print (e)
            if e.args[0] == 1062:
                return "Duplicate entry '{}' for NHTSA".format(nhtsa)
            else:
                return str(e)
        finally:
            print (query)

    @classmethod
    def search_vehicle(cls, vin, model_year, vehicle_type_name, manufacturer_name, color, keyword, sortby, filter, internal=False):
        filter_dict = {'all' : '', 
                       'sold' : 'Buy.sales_date IS NOT NULL AND ', 
                       'unsold' : 'Buy.sales_date IS NULL AND '}
        if internal:
            query = "SELECT Vehicle.vin AS vehicle_vin,\
                            Vehicle.vehicle_type_name AS vehicle_type_name,\
                            Vehicle.model_year AS model_year,\
                            Vehicle.manufacturer_name AS manufacturer_name,\
                            Vehicle.mileage AS mileage,\
                            Vehicle.cost_price AS cost_price,\
                            Vehicle.model_name AS model_name,\
                            Vehicle.description AS description,\
                            Buy.sales_date AS sales_date,\
                            GROUP_CONCAT(VehicleColor.color) color_list,\
                            ROUND((IFNULL(C.total_repiar_cost, 0) * 1.10) + (cost_price * 1.10), 2) AS sales_price\
                    FROM\
                            Vehicle LEFT JOIN VehicleColor ON Vehicle.vin = VehicleColor.vin\
                                    LEFT JOIN Buy ON Vehicle.vin = Buy.vin\
                                    LEFT JOIN (SELECT vin, sum(cost) as total_repiar_cost FROM RepairService GROUP BY vin) as C ON Vehicle.vin = C.vin\
                    GROUP BY vehicle_vin HAVING " + filter_dict[filter] +\
                            "((%s <> '' AND Vehicle.vin = %s) OR (%s = '')) AND\
                            ((%s <> '' AND vehicle_type_name = %s) OR (%s = '')) AND\
                            ((%s <> '' AND manufacturer_name = %s) OR (%s = '')) AND\
                            ((%s <> '' AND model_year = %s) OR (%s = '')) AND\
                            ((%s <> '' AND color_list LIKE %s) OR (%s = '') OR color_list IS NULL) AND\
                            (%s <> '' AND (model_year LIKE %s OR description LIKE %s OR model_name LIKE %s OR manufacturer_name LIKE %s) OR (%s = ''))\
                            ORDER BY {0} ASC;".format(sortby)
        else:
            query = "SELECT Vehicle.vin AS vehicle_vin,\
                            Vehicle.vehicle_type_name AS vehicle_type_name,\
                            Vehicle.model_year AS model_year,\
                            Vehicle.manufacturer_name AS manufacturer_name,\
                            Vehicle.mileage AS mileage,\
                            Vehicle.cost_price AS cost_price,\
                            Vehicle.model_name AS model_name,\
                            Vehicle.description AS description,\
                            Buy.sales_date AS sales_date,\
                            GROUP_CONCAT(DISTINCT VehicleColor.color) color_list,\
                            ROUND((C.total_repiar_cost * 1.10) + (cost_price * 1.10), 2) AS sales_price,\
                            RepairService.repair_status AS repair_status\
                    FROM\
                            Vehicle LEFT JOIN RepairService ON Vehicle.vin = RepairService.vin\
                                    LEFT JOIN VehicleColor ON Vehicle.vin = VehicleColor.vin\
                                    LEFT JOIN Buy ON Vehicle.vin = Buy.vin\
                                    LEFT JOIN (SELECT vin, sum(cost) as total_repiar_cost FROM RepairService GROUP BY vin) as C ON Vehicle.vin = C.vin\
                    GROUP BY vehicle_vin HAVING\
                            Buy.sales_date IS NULL AND\
                            repair_status NOT LIKE 'pending' AND\
                            repair_status NOT LIKE 'progress' AND\
                            ((%s <> '' AND Vehicle.vin = %s) OR (%s = '')) AND\
                            ((%s <> '' AND vehicle_type_name = %s) OR (%s = '')) AND\
                            ((%s <> '' AND manufacturer_name = %s) OR (%s = '')) AND\
                            ((%s <> '' AND model_year = %s) OR (%s = '')) AND\
                            ((%s <> '' AND color_list LIKE %s) OR (%s = '') OR color_list IS NULL) AND\
                            (%s <> '' AND (model_year LIKE %s OR description LIKE %s OR model_name LIKE %s OR manufacturer_name LIKE %s) OR (%s = ''))\
                    ORDER BY {0} ASC;".format(sortby)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                fquery = cur.mogrify(query, (vin, vin, vin,
                                    vehicle_type_name, vehicle_type_name, vehicle_type_name,
                                    manufacturer_name, manufacturer_name, manufacturer_name,
                                    model_year, model_year, model_year,
                                    color, '%'+color+'%', color,
                                    '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
                cur.execute(query, (vin, vin, vin,
                                    vehicle_type_name, vehicle_type_name, vehicle_type_name,
                                    manufacturer_name, manufacturer_name, manufacturer_name,
                                    model_year, model_year, model_year,
                                    color, '%'+color+'%', color,
                                    '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
                cls.conn.commit()
            if not cur:
                return "No vehicle found"
            res = cur.fetchall()
            print('res', res)
            return res
        except Exception as e:
            print('line 274 e: ', e)
            return str(e)
        finally:
            print(fquery)

    @classmethod
    def calculate_available_vehicle(cls):
        query = "SELECT COUNT(T.vin) AS c FROM (\
                    SELECT vehicle.vin,\
                           GROUP_CONCAT(repairservice.repair_status) AS repair_status,\
                           buy.sales_date AS sales_date\
	                FROM vehicle\
                    LEFT JOIN repairservice ON vehicle.vin = repairservice.vin\
                    LEFT JOIN buy ON vehicle.vin = buy.vin\
	                GROUP BY vehicle.vin\
	                HAVING\
	                repair_status NOT LIKE '%pending%' AND\
	                repair_status NOT LIKE '%progress%' AND\
                    sales_date IS NULL) AS T"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                cls.conn.commit()
                res = cur.fetchall()
            return res
        except Exception as e:
            return str(e)
        finally:
            print(query)

    @classmethod
    def calculate_repairing_vehicle(cls):
        query = "SELECT COUNT(T.vin) AS c FROM (\
                    SELECT vehicle.vin,\
				    GROUP_CONCAT(repairservice.repair_status) AS repair_status,\
                    buy.sales_date AS sales_date\
	                FROM vehicle LEFT JOIN repairservice ON vehicle.vin = repairservice.vin\
                                 LEFT JOIN buy ON vehicle.vin = buy.vin\
	                GROUP BY vehicle.vin HAVING\
	                (repair_status LIKE '%pending%' OR\
                    repair_status LIKE '%progress%') AND\
                    sales_date IS NULL) AS T"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                cls.conn.commit()
                res = cur.fetchall()
            return res
        except Exception as e:
            return str(e)
        finally:
            print(query)
    
    @classmethod
    def calculate_unsold_vehicle(cls):
        query = "SELECT COUNT(T.vin) AS c FROM\
                    (SELECT vehicle.vin,\
                    buy.sales_date AS sales_date\
	                FROM vehicle LEFT JOIN buy ON vehicle.vin = buy.vin\
	                WHERE sales_date IS NULL) AS T"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                cls.conn.commit()
                res = cur.fetchall()
            return res
        except Exception as e:
            return str(e)
        finally:
            print(query)

    @classmethod
    def vehicle_detail(cls, vin):
        query = "SELECT Vehicle.model_name AS model_name,\
                        Vehicle.model_year AS model_year,\
                        Vehicle.car_condition AS car_condition,\
                        Vehicle.mileage AS mileage,\
                        Vehicle.description AS description,\
                        Vehicle.vehicle_type_name AS vehicle_type_name,\
                        Vehicle.manufacturer_name AS manufacturer_name,\
                        Vehicle.cost_price AS cost_price,\
                        Vehicle.invent_start_dt AS invent_start_dt,\
                        Vehicle.username AS clerk,\
                        Vehicle.customerID AS seller_customerID,\
                        Buy.username AS salesperson,\
                        Buy.sales_date AS sales_date,\
                        Buy.customerID AS buyer_customerID,\
                        ROUND((C.total_repiar_cost * 1.10) + (cost_price * 1.10), 2) AS sales_price\
                 FROM\
                        Vehicle LEFT JOIN Buy ON Vehicle.vin = Buy.vin\
                        LEFT JOIN (SELECT vin, sum(cost) as total_repiar_cost FROM RepairService GROUP BY vin) as C ON Vehicle.vin = C.vin\
                 WHERE Vehicle.vin = %s;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                fquery = cur.mogrify(query, (vin))
                cur.execute(query, (vin))
                cls.conn.commit()
                res = cur.fetchall()
            return res
        except Exception as e:
            return str(e)
        finally:
            print(fquery)

    @classmethod
    def view_internaluser_information(cls, username):
        query = "SELECT InternalUser.first_name AS first_name,\
                        InternalUser.last_name AS last_name\
                 FROM\
                        InternalUser\
                 WHERE InternalUser.username = %s;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                fquery = cur.mogrify(query, (username))
                cur.execute(query, (username))
                cls.conn.commit()
                res = cur.fetchall()
            return res
        except Exception as e:
            return str(e)
        finally:
            print(fquery)

    @classmethod
    def add_vehicle(cls, vin, model_name, model_year, cost_price, invent_start_dt, car_condition, mileage, description, username,
                    customerID, vehicle_type_name, manufacturer_name, colors):
        query = ""
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                query = "INSERT INTO Vehicle (vin, model_name, model_year, cost_price, invent_start_dt, car_condition, mileage, description, username, customerID, vehicle_type_name, manufacturer_name) \
                VALUES (%s, %s, YEAR(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cur.execute(query, (vin, model_name, model_year, cost_price, invent_start_dt, car_condition, mileage, description, username,
                    customerID, vehicle_type_name, manufacturer_name))
                input_args = []
                query = "INSERT INTO VehicleColor (vin, color) VALUES (%s, %s);"
                for color in colors:
                    input_args.append((vin, color))
                cur.executemany(query,input_args)
                cls.conn.commit()
                cur.close()
            return "Add vehicle '{}' successfully".format(vin), vin
        except Exception as e:
            cls.conn.rollback()
            print(e)
            if e.args[0] == 1062:
                return "VIN '{}' already exist in the inventroy".format(vin), None
            else:
                return str(e), None
        finally:
            print(query)

## Seller Histroy Report
    @classmethod
    def seller_history_report(cls):
        query = \
        "SELECT Customer_list.customer_name,\
                COUNT(Vehicle.vin) AS total_number_vehicles_sold,\
                AVG(Vehicle.cost_price) AS average_purchase_price,\
                (CASE\
                    WHEN SUM(RepairPerVehicle.sum_repairs)/count(Vehicle.vin) IS NULL THEN 0\
                    ELSE SUM(RepairPerVehicle.sum_repairs)/count(Vehicle.vin)\
                 END)AS average_repairs\
                FROM\
                ((SELECT customerID,\
                CONCAT(Individual.first_name, ' ', Individual.last_name) AS customer_name\
         FROM Individual)\
         UNION\
         (SELECT customerID,\
                 company_name AS customer_name\
          FROM Business)) AS Customer_list\
          LEFT JOIN Vehicle\
          ON Customer_list.customerID = Vehicle.customerID\
         LEFT JOIN\
         (SELECT vin,\
                 count(serviceID) AS sum_repairs\
          FROM RepairService\
          GROUP BY vin) AS RepairPerVehicle\
         ON Vehicle.vin = RepairPerVehicle.vin\
         GROUP BY Customer_list.customer_name\
         ORDER BY COUNT(Vehicle.vin) DESC, SUM(RepairPerVehicle.sum_repairs)/count(Vehicle.vin) ASC;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

## Inventory Age Report
    @classmethod
    def inventory_age_report(cls):
        query = \
            '''
            SELECT
                vehicle_type_name,
                MIN(DATEDIFF(CURDATE(), invent_start_dt)) as minimum_days_in_inventory,
                AVG(DATEDIFF(CURDATE(), invent_start_dt)) as average_days_in_inventory,
                MAX(DATEDIFF(CURDATE(), invent_start_dt)) as maximum_days_in_inventory
            FROM
            (SELECT Vehicle.vin,
                            Vehicle.vehicle_type_name,
                            Vehicle.invent_start_dt,
                            Buy.sales_date
            FROM Vehicle
            LEFT JOIN Buy
            ON Vehicle.vin = Buy.vin) AS Inventory
            WHERE ISNULL(sales_date) = 1
            GROUP BY vehicle_type_name;
            '''
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            return result
        except Exception as e:
            print (e)
        finally:
            print ('Generate Inventory Age Report')

## Average Time in Inventory Report
    @classmethod
    def average_inventory_report(cls):
        query = \
            '''
            SELECT
                vehicle_type_name,
                AVG(DATEDIFF(sales_date, invent_start_dt)) AS average_days_in_inventory
            FROM
                (SELECT
                    Vehicle.vin,
                    Vehicle.vehicle_type_name,
                    Vehicle.invent_start_dt,
                    Buy.sales_date
                FROM Vehicle
                LEFT JOIN Buy
                ON Vehicle.vin = Buy.vin) AS Inventory
            WHERE ISNULL(sales_date) = 0
            GROUP BY vehicle_type_name;
            '''
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
            return result
        except Exception as e:
            print (e)
        finally:
            print ('Generate Average Time in Inventory Report')

## Price Per Condition Report
    @classmethod
    def price_per_condition(cls):
        query = \
        "SELECT Excellent.vehicle_type_name,\
               (CASE\
                          WHEN ISNULL(Excellent.Excellent) = 1 THEN 0\
                          ELSE Excellent.Excellent\
                 END) as Excellent,\
                (CASE\
                          WHEN ISNULL(Very_Good.Very_Good) = 1 THEN 0\
                          ELSE Very_Good.Very_Good\
                 END) as Very_Good,\
                (CASE\
                          WHEN ISNULL(Good.Good) = 1 THEN 0\
                          ELSE Good.Good\
                 END) as Good,\
                         (CASE\
                          WHEN ISNULL(Fair.Fair) = 1 THEN 0\
                          ELSE Fair.Fair\
                 END) as Fair\
         FROM\
         (SELECT vehicle_type_name,\
                 AVG(cost_price) AS Excellent\
          FROM Vehicle\
          WHERE car_condition = 'Excellent'\
          GROUP BY vehicle_type_name) AS Excellent\
         LEFT OUTER JOIN\
         (SELECT vehicle_type_name,\
                 AVG(cost_price) AS Very_Good\
          FROM Vehicle\
          WHERE car_condition = 'Very Good'\
          GROUP BY vehicle_type_name) AS Very_Good\
         ON Excellent.vehicle_type_name = Very_Good.vehicle_type_name\
         LEFT OUTER JOIN\
         (SELECT vehicle_type_name,\
                 AVG(cost_price) AS Good\
          FROM Vehicle\
          WHERE car_condition = 'Good'\
          GROUP BY vehicle_type_name) AS Good\
         ON Excellent.vehicle_type_name = Good.vehicle_type_name\
         LEFT OUTER JOIN\
         (SELECT vehicle_type_name,\
                 AVG(cost_price) AS Fair\
          FROM Vehicle\
          WHERE car_condition = 'Fair'\
          GROUP BY vehicle_type_name) AS Fair\
         ON Excellent.vehicle_type_name = Fair.vehicle_type_name;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

## Repair Statistics Report
    @classmethod
    def repair_statistics(cls):
        query = \
        "SELECT vendor_name,\
                COUNT(serviceID) as number_of_repairs_completed,\
                SUM(cost) AS total_cost_spent,\
                (COUNT(serviceID)/COUNT(DISTINCT vin)) AS average_repairs_per_vehicle,\
                AVG(DATEDIFF(end_date, start_date))  AS average_service_days\
         FROM RepairService\
         WHERE repair_status = 'completed'\
         GROUP BY vendor_name;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

# Monthly Sales Report
    @classmethod
    def monthly_sales(cls):
        query = \
        "SELECT YEAR(Buy.sales_date) AS year,\
                MONTH(Buy.sales_date) AS month,\
                COUNT(Buy.vin) AS total_number_of_vehicles_sold,\
                SUM(Buy.sales_price) AS total_sales_income,\
                SUM(Buy.sales_price - Vehicle.cost_price - RepairService.cost) AS total_net_income\
        FROM Buy LEFT JOIN Vehicle on Buy.vin = Vehicle.vin\
        LEFT JOIN RepairService on Buy.vin = RepairService.vin\
        GROUP BY YEAR(Buy.sales_date), MONTH(Buy.sales_date)\
        HAVING total_number_of_vehicles_sold > 0\
        ORDER BY year DESC, month DESC;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print (query)

    @classmethod
    def check_repair(cls,vin,start_date,end_date):
        query = "SELECT vin FROM repairservice where vin =%s and %s <= end_date and %s >=start_date"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query,(vin, start_date,end_date))
                result = cur.fetchall()
                if result:
                    return True
                else:
                    return False
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

# Yearly Sales Rank
    @classmethod
    def yearly_sales_rank(cls, year):
        query = \
        "SELECT CONCAT(InternalUser.first_name, ' ', InternalUser.last_name) as name,\
                COUNT(Buy.vin) as total_vehicles_sold,\
                SUM(Buy.sales_price) as total_sales\
         FROM Buy \
         LEFT JOIN InternalUser\
         ON Buy.username = InternalUser.username\
         WHERE YEAR(Buy.sales_date) = {} and Buy.username <> 'burdell'\
         GROUP BY CONCAT(InternalUser.first_name, ' ', InternalUser.last_name);".format(year)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

# Monthly Sales Rank
    @classmethod
    def monthly_sales_rank(cls, year, month):
        query = \
        "SELECT CONCAT(InternalUser.first_name, ' ', InternalUser.last_name) as name,\
                COUNT(Buy.vin) as total_vehicles_sold,\
                SUM(Buy.sales_price) as total_sales\
         FROM Buy\
         LEFT JOIN InternalUser\
         ON Buy.username = InternalUser.username\
         WHERE YEAR(Buy.sales_date) = {} and MONTH(Buy.sales_date) = {} and Buy.username <> 'burdell'\
         GROUP BY CONCAT(InternalUser.first_name, ' ', InternalUser.last_name)".format(year, month)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
                return result
        except Exception as e:
            print (e)
        finally:
            print ('Query Successful')

    @classmethod
    def get_customer_type(cls, _id):
        query = "SELECT Individual.customerID FROM Individual WHERE customerID = {}".format(_id)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
            if not result:
                return "Business"
            else:
                return "Individual"
        except Exception as e:
            print (e)
            return str(e), None
        finally:
            print (query)

    @classmethod
    def get_customer_by_customer_id(cls, customer_type, _id):
        query = ""
        if (customer_type == 'Individual'):
            query = \
                '''
                SELECT Individual.customerID, driver_license_num, CONCAT(first_name, ' ', last_name) as customer_name,
                    email, phone_num, street, city, state, zip_code 
                FROM Individual LEFT JOIN Customer 
                ON Individual.customerID = Customer.customerID 
                WHERE Individual.customerID = {}
                '''.format(_id)
        else:
            query = "SELECT Business.customerID,\
                            TIN,\
                            company_name as customer_name,\
                            primary_contact,\
                            primary_contact_title,\
                            email, phone_num, street, city, state, zip_code\
                    FROM Business LEFT JOIN Customer\
                    ON Business.customerID = Customer.customerID\
                    WHERE Business.customerID = {}".format(_id)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
            if not result:
                return "No record found", result
            else:
                return result
        except Exception as e:
            print (e)
            return str(e), None
        finally:
            print (query)

    @classmethod
    def get_customer(cls, customer_type, id):
        query = ""
        if (customer_type == 'Individual'):
            query = \
                '''
                SELECT Individual.customerID, driver_license_num, CONCAT(first_name, ' ', last_name) as customer_name,
                    email, phone_num, street, city, state, zip_code
                FROM Individual LEFT JOIN Customer
                ON Individual.customerID = Customer.customerID
                WHERE driver_license_num=%s
                '''
        else:
            query = \
                '''
                SELECT Business.customerID, TIN, company_name as customer_name, primary_contact, primary_contact_title,
                    email, phone_num, street, city, state, zip_code
                FROM Business LEFT JOIN Customer
                ON Business.customerID = Customer.customerID
                WHERE TIN=%s
                '''
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (id))
                result = cur.fetchone()
            if not result:
                return "No record found", result
            else:
                return "Found customer with ID '{}'".format(result["customerID"]), result
        except Exception as e:
            print (e)
            return str(e), None
        finally:
            print (query)

    @classmethod
    def add_individual_customer(cls, email, phone_num, street, city, state, zip_code,
            driver_license_num, first_name, last_name):
        customer_query = \
            "INSERT INTO Customer (email, phone_num, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s);"
        individual_query = \
            "INSERT INTO Individual (customerID, driver_license_num, first_name, last_name) VALUES (LAST_INSERT_ID(), %s, %s, %s);"
        query = "SELECT customerID, CONCAT(first_name, ' ', last_name) as customer_name FROM Individual WHERE driver_license_num=%s;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(customer_query, (email, phone_num, street, city, state, zip_code))
                cur.execute(individual_query, (driver_license_num, first_name, last_name))
                cls.conn.commit()
                cur.execute(query, (driver_license_num))
                result = cur.fetchone()
                cur.close()
            return "Add customer '{} {}' successful".format(first_name, last_name), result
        except Exception as e:
            print (e)
            return str(e), False
        finally:
            print (customer_query, individual_query)

    @classmethod
    def add_business_customer(cls, email, phone_num, street, city, state, zip_code,
            TIN,company_name,primary_contact,primary_contact_title):
        customer_query = \
            "INSERT INTO Customer (email, phone_num, street, city, state, zip_code) VALUES (%s, %s, %s, %s, %s, %s);"
        business_query = \
            "INSERT INTO Business (customerID,TIN,company_name,primary_contact,primary_contact_title) \
             VALUES(LAST_INSERT_ID(), %s, %s, %s, %s);"
        query = "SELECT customerID, company_name as customer_name FROM Business WHERE TIN=%s;"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(customer_query, (email, phone_num, street, city, state, zip_code))
                cur.execute(business_query, (TIN,company_name,primary_contact,primary_contact_title))
                cls.conn.commit()
                cur.execute(query, (TIN))
                result = cur.fetchone()
            return "Add customer '{}' successful".format(company_name), result
        except Exception as e:
            print (e)
            return str(e), None
        finally:
            print (customer_query, business_query)

    @classmethod
    def calculate_sales_price(cls, vin):
        query = \
            '''
            SELECT V.vin, V.cost_price, C.total_repiar_cost,
                ROUND((COALESCE(C.total_repiar_cost, 0) * 1.10) + (V.cost_price * 1.25), 2) AS sales_price
            FROM Vehicle as V LEFT JOIN
            (SELECT vin, sum(cost) as total_repiar_cost FROM RepairService GROUP BY vin) as C
            ON V.vin = C.vin
            WHERE V.vin = %s;
            '''
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (vin))
                result = cur.fetchone()
            print(result)
            if not result:
                return "No record found", result
            else:
                return "Record found", round(float(result['sales_price']),  2)
        except Exception as e:
            print (e)
            return str(e), None
        finally:
            print (query)

    @classmethod
    def record_sales(cls, customerID, username, vin, sales_price, sales_date):
        query = "INSERT INTO Buy (customerID, username, vin, sales_price, sales_date) VALUES (%s, %s, %s, %s, %s);"
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query, (customerID, username, vin, sales_price, sales_date))
                cls.conn.commit()
            return "Record sales order successful for {}".format(vin)
        except Exception as e:
            print (e)
            if e.args[0] == 1062:
                return "Vehicle '{}' already sold".format(vin)
            else:
                return str(e)
        finally:
            print (query)

    @classmethod
    def add_repair(cls,vin, start_date, end_date,description, cost, vendor_name):
        query = "INSERT INTO repairservice (vin,start_date, end_date, description, cost, vendor_name,repair_status)\
                 VALUES(%s, %s,%s, %s,%s, %s,'pending');"
        print (query)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query,(vin, start_date, end_date,description, cost, vendor_name))
                cls.conn.commit()
            return True
        except Exception as e:
            print (e)
            return False
        finally:
            print ('Query Successful')

    @classmethod
    def add_vendor(cls, vendorname, phone, street, city, zipcode, state):
        query = "INSERT INTO vendor(vendor_name, phone, street, zip_code, state, city) \
                 VALUES(%s, %s,%s, %s,%s, %s);"
        print (query)
        try:
            cls.conn.ping()
            with cls.conn.cursor() as cur:
                cur.execute(query,(vendorname, phone, street,city, zipcode, state))
                cls.conn.commit()
            return True
        except Exception as e:
            print (e)
            return False
        finally:
            print ('Query Successful')

