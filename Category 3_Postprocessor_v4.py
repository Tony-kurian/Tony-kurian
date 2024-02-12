import json
import re
from jsonschema._format import is_date

water_water = ["conservation", "edwards aquifer", "water charges", "water", "landfill dev. fee", "water", "water", "water", "water", "lsgwcd fee", "sjra fee", "water", "water 1", "water 2", "water", "wa: franchise fee", "water", "water", "water", "water", "water 2", "water", "late fee", "water", "parks fee", "water", "past due amount", "water", "utgcd", "water", "water meter 83236994", "water meter 83237003", "eaa fee", "wa res fee", "water", "water 2", "utgcd", "water", "water", "st mnt fee", "water", "late fee", "water minimum charge", "water usage charge", "tif", "water", "late fee", "water", "water 2", "past due", "water", "water", "water base", "paving assmt", "water usage", "water"]
water_sewer = ["sewer", "surcharge", "sewer charges", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer","sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer", "sewer","sewer", "sewer", "grease trap", "sewer", "ww minimum charge", "ww service charge", "sewer","sewer", "sewer", "sewer", "sewer base", "sewer costs", "sewer", "sewer", "wastewater costs","sewer", "sewer permit fee", "sewer user fee", "sw capacity charge", "sw usage charge", "sewer","greas trap inspections", "sewer", "grease trap", "sewer", "sewer", "grease trap", "sewer","sewer", "grease trap inspection", "sewer", "sewer", "grease trap", "sewer", "grease trap","sewer", "basic sewer", "sewer"]
water_drainage = ["drainage chg","drainage","storm water","storm drainage","storm utility fee","storm water fee","storm drainage","drainage utility fee","drainage fee","stormwater"]
water_fireline = ["fire line", "fire line"]
water_brush = ["brush", "tax", "br: brush"]
water_irrigation = ["sprinkler","irrigation","lsgwcd fee","sjra fee","sprinkler 1","parks fee","sprinkler usage","ground water","ir: administrative fee","irrigation usage","late fee","irrigation capacity","letter fee","penalty","ir- tax","ir-water authority","ir-water conservation","lsgw/sjra","ir: water auth","basic irrigation","ir: regulatory asmt"]
electric_electric = ["electric", "elec wires", "elec energy", "sec light", "sales tax", "electric","fuel adjustment", "local charge", "Customer charge", "energy charge", "pcrf commercial"]
electric_power = ["demand", "demand charge"]
street_street = ["Street fee"]
natural_gas_natural_gas = ["gas Service", "gas distr.", "gas commodty", "gas","fuel adj", "gas", "gas", "gas", "sales tax", "cost of Gas","delivery charge", "franchise tax", "gross receipt tax", "rider","service charge"]
garbage_garbage = ["garbage", "sales tax", "garbage", "garbage 2", "garbage 3", "tax", "garbage", "solid waste tax","garbage", "taxes", "tax", "garbage", "garbage", "garbage", "sales tax", "garbage", "tax", "garbage", "compactors"]
charges_check = ['sewer', 'surcharge', 'conservation', 'edwards aquifer', 'water', 'garbage', 'sales tax', 'brush','water', 'sewer', 'tax', 'sewer', 'landfill dev. fee', 'water', 'sprinkler', 'sewer', 'water','drainage chg', 'sewer', 'fire line', 'water', 'electric', 'elec wires', 'elec energy', 'gas service','gas distr.', 'gas commodty', 'sec light', 'sales tax', 'sewer', 'water', 'garbage', 'garbage 2','garbage 3', 'gas', 'fuel adj', 'tax', 'irrigation', 'lsgwcd fee', 'sjra fee', 'sewer', 'lsgwcd fee','sjra fee', 'water', 'drainage', 'sprinkler 1', 'sewer', 'water 1', 'water 2', 'garbage', 'w-water','roll off per ton', 'compactor charge', 'solid waste tax', 'irrigation', 'sewer', 'storm water','water', 'sewer', 'wa: franchise fee', 'water', 'gas', 'storm drainage', 'sewer', 'fire line','water', 'fire prot', 'sewer', 'water', 'garbage', 'taxes', 'sewer', 'tax', 'water', 'water 2','garbage', 'tuf', 'irrigation', 'sewer', 'water', 'tax', 'sewer', 'late fee', 'water', 'irrigation','parks fee', 'sewer', 'parks fee', 'water', 'sprinkler', 'sewer', 'past due amount', 'water','sewer', 'utgcd', 'water', 'water meter 83236994', 'water meter 83237003', 'sewer', 'eaa fee','wa res fee', 'water', 'water 2', 'garbage', 'electric', 'demand', 'irrigation', 'storm utility fee','sewer', 'utgcd', 'water', 'sewer', 'water', 'garbage', 'sales tax', 'irrigation', 'grease trap','sewer', 'st mnt fee', 'storm water fee', 'tax', 'street fee', 'water', 'sprinkler', 'sprinkler usage',
    'ww minimum charge', 'ww service charge', 'late fee', 'storm drainage', 'water minimum charge',
    'water usage charge', 'sprinkler', 'sewer', 'drainage utility fee', 'tif', 'water', 'fuel adjustment',
    'local charge', 'sewer', 'late fee', 'water', 'water 2', 'gas', 'sewer', 'past due', 'water', 'sewer',
    'sewer base', 'sales tax', 'sanit/street', 'sanitation', 'water', 'water base', 'sewer costs',
    'paving assmt', 'water usage', 'irrigation', 'sewer', 'water', 'garbage', 'tax', 'ground water',
    'ir: administrative fee', 'irrigation', 'sewer', 'administrative fee', 'grease trap fee', 'ground water',
    'water', 'drainage fee', 'irrigation usage', 'late fee', 'water usage', 'wastewater costs',
    'late fee - water', 'surcharge pretreatment', 'water usage', 'br: brush', 'irrigation', 'water',
    'sewer', 'stormwater', 'garbage', 'stormwater', 'irrigation capacity', 'irrigation usage',
    'sewer permit fee', 'sewer user fee', 'sw capacity charge', 'sw usage charge', 'wa capacity charge',
    'wa usage charge', 'customer charge', 'demand charge', 'energy charge', 'pcrf commercial', 'sewer',
    'eaa mgt fee', 'eea cons fee', 'water 1', 'water 2', 'water rights fee', 'gas', 'sales tax',
    'compactors', 'greas trap inspections', 'sewer', 'late fee', 'water', 'water authority', 'grease trap',
    'sewer', 'water', 'wtr auth', 'irrigation', 'letter fee', 'penalty', 'sewer', 'inspection fee',
    'letter fee', 'nhcrwa', 'penalty', 'water', 'water authority', 'grease trap', 'water charges',
    'sewer charges', 'whcrwa', 'grease trap', 'sewer', 'harris co wtr auth', 'water', 'ir- tax',
    'irrigation', 'sewer', 'fire line', 'wa- tax', 'water', 'irrigation', 'ir-water authority',
    'ir-water conservation', 'grease trap inspection', 'sewer', 'water', 'water authority',
    'water conservation', 'irrigation', 'lsgw/sjra', 'sewer', 'inspections', 'lsgw/sjra', 'water',
    'ir: water auth', 'irrigation', 'grease trap', 'sewer', 'balance forward', 'late fee', 'letter fee',
    'mics credit', 'misc credit', 'water', 'wtr auth', 'grease trap', 'sewer', 'beginning balance',
    'nhcrwa', 'water', 'basic irrigation', 'ir: regulatory asmt', 'irrigation', 'late fee', 'basic sewer',
    'sewer', 'basic water', 'late fee', 'regulatory asmt', 'water'
]

def retrieve_foi_entities(data):
    base_location = (data['hits']['hits'][0]['_source']['data'])
    field_names = ['from_date','to_date']
    fields = {}
    for d in base_location:
        if d['field'] == 'from_date':
            if 'answer' in d and len(d['answer']) > 0:
                from_date = "".join(answer["text"] for answer in d['answer'])
                fields['from_date'] = from_date
        if d['field'] == 'to_date':
            if 'answer' in d and len(d['answer']) > 0:
                to_date = "".join(answer["text"] for answer in d['answer'])
                fields['to_date'] = to_date
    return fields

def get_table_type(table_content):
    table_type = ""
    if table_content['table_identified'] == 'charges_table' and table_content.get("table_data"):
        table_type = "charges_table"
    elif table_content['table_identified'] == "meter_table" and table_content.get("table_data"):
        table_type = "meter_table"
    else:
        for i, row in enumerate(table_content['table_data']):
            stripped_values = [value.strip() for value in row.values()]
            if any(x.lower() in stripped_values for x in ['water', 'sewer', 'tax','garbage']):
                table_type = "charges_table"
                break
            elif any(x.lower() in stripped_values for x in ['current', 'previous', 'usage','meter','reading']):
                table_type = "meter_table"
                break
    return table_type


def process_meter_table(table_content, smartextract_jsons):
    idx_to_remove = []
    dates = []
    numerics = []
    usage = []
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')  # Adjust the pattern based on your date format
    numeric_pattern = re.compile(r'\d+(\.\d+)?')  # Adjust the pattern based on your numeric format
    Start_date = False
    End_date = False
    for idx, row in enumerate(table_content["table_data"]):
        stripped_values = [value.strip() for value in row.values()]
        if any(x in stripped_values[0].lower() for x in ['current', 'previous', 'usage', 'meter number', 'reading', 'date']):
            idx_to_remove.append(idx)
    table_content["table_data"] = [j for i, j in enumerate(table_content["table_data"]) if i not in idx_to_remove]
    for element in table_content['table_data']:
        for element_entity in element.items():
            key, value = element_entity
            if re.match(date_pattern, str(value)):
                dates.append(value)
            elif re.match(numeric_pattern, str(value)):
                numerics.append(value)
            else:
                usage.append(value)
        # Now you have separate arrays for dates, numerics, and usage
        print("Dates:", dates)
        print("Numerics:", numerics)
        print("Usage:", usage)

        result = retrieve_foi_entities(smartextract_jsons)
        table_content['table_data'][0]["6"] = result['from_date']
        table_content['table_data'][0]["5"] = result['to_date']
    header_row = {
        "0": "c3mst", "1": "c3mN", "2": "c3mRP", "3": "c3mRC",
        "4": "c3ubm", "5": "c3sped", "6": "c3spsd", "7": "c3msst",
        "8": "c3uom", "9": "c3mm", "10": "c3pf", "11": "c3du"
    }
    table_content.get("table_data").insert(0, header_row)
    print("Updated meter table:")
    for row in table_content['table_data']:
        print(row)

def process_charge_table(table_content):
    idx_to_remove = []
    remove_date_index = []
    for idx, row in enumerate(table_content["raw_table_data"]):
        stripped_values = [value.strip() for value in row.values()]
        if any(x.lower() in stripped_values[0] for x in ['water', 'sewer', 'tax fee']):
            idx_to_remove.append(idx)
    table_content["raw_table_data"] = [j for i, j in enumerate(table_content["raw_table_data"]) if i not in idx_to_remove]
    if table_content["raw_table_data"]:
        for element in table_content['raw_table_data']:
            value = element.get('0')
            if (value is not None and value in charges_check and not value.isdigit() and not re.match(r'\d{1,2}/\d{1,2}/\d{4}', value)):
                continue
            else:
                del element['0']
            table_content["raw_table_data"] = [element for element in table_content["raw_table_data"] if
                                               any(value.strip() for value in element.values())]

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
        elif row['1'].lower().strip() in [value.strip().lower() for value in electric_electric]:
            row["3"] = "Electric"
            row["4"] = "Electric"
        elif row['1'].lower().strip() in [value.strip().lower() for value in electric_power]:
            row["3"] = "Electric"
            row["4"] = "Power"
        elif row['1'].lower().strip() in [value.strip().lower() for value in street_street]:
            row["3"] = "Street"
            row["4"] = "Street"
        elif row['1'].lower().strip() in [value.strip().lower() for value in natural_gas_natural_gas]:
            row["3"] = "Natural Gas"
            row["4"] = "Natural Gas"
        else:
            row["3"] = ""
            row["4"] = ""
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
    table_content.get("raw_table_data").insert(0, header_row)
    print("Updated charge table:")
    for row in table_content['raw_table_data']:
        print(row)

def process_table_data(input_tables_data,smartextract_jsons):
    charges_table_found = False
    meter_table_found = False
    for table_id, table_content in input_tables_data.items():
        table_type = get_table_type(table_content)
        print(table_type)
        if str(table_type).strip() == "meter_table":
            process_meter_table(table_content,smartextract_jsons)
        if str(table_type).strip() == "charges_table":
            process_charge_table(table_content)
    print("All finished.")

def run(input_tables_data, smartextract_jsons):
    process_table_data(input_tables_data,smartextract_jsons)



if __name__=='__main__':
    #table_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\70230001_Table.json"
    #foi_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\70230001_Foi.json"
    #table_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Table\0020001390005_Table.json"
    #foi_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Foi\0020001390005_Foi.JSON"
    table_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Table\046935272003_Table.json"
    foi_file = r"C:\Users\248740\PycharmProjects\HEB POST PROCESSOR\Foi\046935272003_Foi.json"
    with open(table_file) as fp:
        input_tables_data = json.load(fp)
    with open(foi_file) as ffp:
        smartextract_jsons = json.load(ffp)
    run(input_tables_data, smartextract_jsons)
