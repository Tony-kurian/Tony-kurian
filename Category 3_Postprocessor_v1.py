import json
import re

water_water = ["conservation", "edwards aquifer", "water charges", "water", "landfill dev. fee", "water", "water",
               "water", "water", "lsgwcd fee", "sjra fee", "water", "water 1", "water 2", "water", "wa: franchise fee",
               "water", "water", "water", "water", "water 2", "water", "late fee", "water", "parks fee", "water",
               "past due amount", "water", "utgcd", "water", "water meter 83236994", "water meter 83237003", "eaa fee",
               "wa res fee", "water", "water 2", "utgcd", "water", "water", "st mnt fee", "water", "late fee",
               "water minimum charge", "water usage charge", "tif", "water", "late fee", "water", "water 2", "past due",
               "water", "water", "water base", "paving assmt", "water usage", "water"]
water_sewer = ["sewer", "surcharge", "sewer charges", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer",
               "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer",
               "sewer", "grease trap", "sewer", "ww minimum charge", "ww service charge", "sewer", "sewer", "sewer",
               "sewer", "sewer base", "sewer costs", "sewer", "sewer", "wastewater costs", "sewer", "sewer permit fee",
               "sewer user fee", "sw capacity charge", "sw usage charge", "sewer", "greas trap inspections", "sewer",
               "grease trap", "sewer", "sewer", "grease trap", "sewer", "sewer", "grease trap inspection", "sewer",
               "sewer", "grease trap", "sewer", "grease trap", "sewer", "basic sewer", "sewer"]
water_drainage = ["drainage chg", "drainage", "storm water", "storm drainage", "storm utility fee", "storm water fee",
                  "storm drainage", "drainage utility fee", "drainage fee", "stormwater"]
water_fireline = ["fire line", "fire line"]
water_brush = ["brush", "tax", "br: brush"]
water_irrigation = ["sprinkler", "irrigation", "lsgwcd fee", "sjra fee", "sprinkler 1", "parks fee", "sprinkler usage",
                    "ground water", "ir: administrative fee", "irrigation usage", "late fee", "irrigation capacity",
                    "letter fee", "penalty", "ir- tax", "ir-water authority", "ir-water conservation", "lsgw/sjra",
                    "ir: water auth", "basic irrigation", "ir: regulatory asmt"]
garbage_garbage = ["garbage", "sales tax", "garbage", "garbage 2", "garbage 3", "tax", "garbage", "solid waste tax",
                   "garbage", "taxes", "tax", "garbage", "garbage", "garbage", "sales tax", "garbage", "tax", "garbage",
                   "compactors"]


# To retrieve_foi_entities ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def retrieve_foi_entities(data):
    base_location = (data['hits']['hits'][0]['_source']['data'])
    field_names = ['from_date', 'to_date']
    fields = {}
    for d in base_location:
        if d['field'] == 'from_date':
            if 'answer' in d and len(d['answer']) > 0:
                from_date = "".join(answer["text"] for answer in d['answer'])
                # print("from_date", from_date)
                fields['from_date'] = from_date

        if d['field'] == 'to_date':
            if 'answer' in d and len(d['answer']) > 0:
                to_date = "".join(answer["text"] for answer in d['answer'])
                # print("to_date", to_date)
                fields['to_date'] = to_date
    # print(fields)
    return fields


# To find the table type --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_table_type(table_content):
    table_type = ""
    if table_content['table_identified'] == 'charges_table' and table_content.get("table_data"):
        table_type = "charges_table"
    elif table_content['table_identified'] == "meter_table" and table_content.get("table_data"):
        table_type = "meter_table"
    else:
        for i, row in enumerate(table_content['table_data']):
            stripped_values = [value.strip() for value in row.values()]
            if any(x.lower() in stripped_values for x in ['water', 'sewer', 'tax', 'garbage']):
                table_type = "charges_table"
                break  # Exit the loop if a match is found in 'cost_table' conditions
            elif any(x.lower() in stripped_values for x in ['current', 'previous', 'usage', 'meter', 'reading']):
                table_type = "meter_table"
                break  # Exit the loop if a match is found in 'meter_table' conditions
    return table_type


# Extracting Data ----------------------------------------------------------------------------------------------------------------------------------------------

def process_charges_data(input_tables_data, smartextract_jsons):
    for table_id, table_content in input_tables_data.items():
        # print(table_content['document_name'])
        table_type = get_table_type(table_content)
        print(table_type)
        # Meter Table -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if str(table_type).strip() == "meter_table":
            idx_to_remove = []
            Start_date = False
            End_date = False
            # Remove rows based on specific conditions
            for idx, row in enumerate(table_content["table_data"]):
                stripped_values = [value.strip() for value in row.values()]
                if any(x in stripped_values[0].lower() for x in
                       ['current', 'previous', 'usage', 'meter number', 'reading', 'date']): idx_to_remove.append(idx)
            # --------------------------------------------- Task on 5/2/2024 ---------------------------------------------------------------------------------------------------------------------
            table_content["table_data"] = [j for i, j in enumerate(table_content["table_data"]) if i not in idx_to_remove]
            #print(table_content["table_data"])
            dates = []
            readings = []
            date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
            numeric_pattern = re.compile(r'[-+]?\d*\.\d+|\d+')
            for row in table_content["table_data"]:
                for value in row.values():
                    # Check if the value is a date
                    date_match = date_pattern.match(value)
                    if date_match:
                        dates.append(value.strip())
                    else:
                        # Try to extract numeric values using regular expression
                        numeric_match = numeric_pattern.match(value.replace(',', ''))
                        if numeric_match:
                            numeric_value = float(numeric_match.group())
                            readings.append(numeric_value)
            # Determine service start and end dates
            service_start_date = min(dates,default=0)
            service_end_date = max(dates,default=0)
            # Determine current and previous readings
            current_reading = max(readings, default=0)
            previous_reading = min(readings, default=0)
            # Calculate usage
            usage_array = [current_reading - previous_reading]
            print("Service Start Date:", service_start_date)
            print("Service End Date:", service_end_date)
            print("Current Reading:", current_reading)
            print("Previous Reading:", previous_reading)
            print("Usage Array:", usage_array)
            table_content["table_data"][0].update({
                'service_start_date': service_start_date,
                'service_end_date': service_end_date,
                'current_reading': current_reading,
                'previous_reading': previous_reading,
                'usage_array': usage_array,
            })
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            header_row = {}
            header_row["0"] = "c3mst"  # serviceType
            header_row["1"] = "c3mN"  # meterNumber
            header_row["2"] = "c3mRP"  # meterReadPrevious
            header_row["3"] = "c3mRC"  # meterReadCurrent
            header_row["4"] = "c3ubm"  # usageByMeter
            header_row["5"] = "c3sped"  # servicePeriodEndDate
            header_row["6"] = "c3spsd"  # servicePeriodStartDate
            header_row["7"] = "c3sst"  # subServiceType
            header_row["8"] = "c3uom"  # uom
            header_row["9"] = "c3mm"  # meterMultiplier
            header_row["10"] = "c3pf"  # powerFactor
            header_row["11"] = "c3du"  # demandUsage'''

            table_content.get("table_data").insert(0, header_row)
            # print("table updated meter table", table_content['table_data'])
            for row in table_content['table_data']:
                print(row)
            print(
                "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    # Charges Table ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if str(table_type).strip() == "charges_table":
        idx_to_remove = []
        for idx, row in enumerate(table_content["raw_table_data"]):
            stripped_values = [value.strip() for value in row.values()]
            if any(x.lower() in stripped_values[0] for x in ['water', 'sewer', 'tax fee']):
                idx_to_remove.append(idx)
        table_content["raw_table_data"] = [j for i, j in enumerate(table_content["raw_table_data"]) if
                                           i not in idx_to_remove]
        remove_date_index = []
        for element in table_content['raw_table_data']:
            for idx, element_entity in element.items():
                match = re.search(r'(\d+/\d+/\d+)', element[idx])
                if match:
                    remove_date_index.append(idx)
            del element[remove_date_index[0]]
        for idx, row in enumerate(table_content["raw_table_data"]):
            if row['1'].lower().strip() in [value.strip().lower() for value in water_water]:
                row["3"] = "Water"
                row["4"] = "Water"
            elif row['1'].lower().strip() in [value.strip().lower() for value in water_sewer]:
                row["3"] = "Water"
                row["4"] = "Storm"
            elif row['1'].lower().strip() in [value.strip().lower() for value in water_irrigation]:
                row["3"] = "Water"
                row["4"] = "Irrigation"
            elif row['1'].lower().strip() in [value.strip().lower() for value in water_drainage]:
                row["3"] = "Water"
                row["4"] = "Drainage"
            elif row['1'].lower().strip() in [value.strip().lower() for value in water_brush]:
                row["3"] = "Water"
                row["4"] = "Brush"
            elif row['1'].lower().strip() in [value.strip().lower() for value in water_fireline]:
                row["3"] = "Water"
                row["4"] = "Fireline"
            elif row['1'].lower().strip() in [value.strip().lower() for value in garbage_garbage]:
                row["3"] = "Garbage"
                row["4"] = "Garbage"
            else:
                row["3"] = ""
                row["4"] = ""
        # table_content['raw_table_data'].insert(0,{"1": "c3Des", "2": "c3Amo", "3": "c3ser", "4": ",c3subs"})
        header_row = {}
        header_row["0"] = "c3mst"  # serviceType
        header_row["1"] = "c3mN"  # meterNumber
        header_row["2"] = "c3mRP"  # meterReadPrevious
        header_row["3"] = "c3mRC"  # meterReadCurrent
        header_row["4"] = "c3ubm"  # usageByMeter
        header_row["5"] = "c3sped"  # servicePeriodEndDate
        header_row["6"] = "c3spsd"  # servicePeriodStartDate
        header_row["7"] = "c3msst"  # subServiceType
        header_row["8"] = "c3uom"  # uom
        header_row["9"] = "c3mm"  # meterMultiplier
        header_row["10"] = "c3pf"  # powerFactor
        header_row["11"] = "c3-du"  # demandUsage'''
        table_content.get("table_data").insert(0, header_row)
        # print("table updated charge table ", table_content['raw_table_data'])
        for row in table_content['raw_table_data']:
            print(row)


# Run Function ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def run(input_tables_data, smartextract_jsons):
    process_charges_data(input_tables_data, smartextract_jsons)


# Main Function __________________________________________________________________________________________________________________
if __name__ == '__main__':
    table_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\70230001_Table.json"
    foi_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\70230001_Foi.json"
    # table_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Table\0020001390005.json"
    # foi_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Foi\0020001390005.JSON"
    with open(table_file) as fp:
        input_tables_data = json.load(fp)
    with open(foi_file) as ffp:
        smartextract_jsons = json.load(ffp)
    run(input_tables_data, smartextract_jsons)
