import json
import uuid


def process_charges_data(input_tables_data):
    for table_id, table_content in input_tables_data.items():
        #Check if the data is in page 1
        table_type = get_table_type(table_content)
        if table_type == "charges":
            # Remove unncessary rows
            idx_to_remove = []
            for idx, row in enumerate(table_content["table_data"]):
                striped_values = [value.strip() for value in row.values()]
                if any(x in striped_values[0] for x in ['DESCRIPTION', 'AMOUNT', 'BALANCE FORWARD', 'PAYMENT']):
                    idx_to_remove.append(idx)
            table_content["table_data"] = [j for i, j in enumerate(table_content["table_data"]) if i not in idx_to_remove]
            for idx, row in enumerate(table_content["table_data"]):
                #if row['0'].lower() == "water":
                row["2"] = "Water"
                row["3"] = "Water"
            table_content['table_data'].insert(0, {"0":"c2des", "1":"c2cost", "2":"aucServ", "3":"aucsst"})

def get_table_type(table_content):
    table_type = ""
    if table_content['table_identified'].strip() == 'charges' and table_content.get("table_data"):
        table_type = "charges"
    elif table_content['table_identified'].strip() == "meter" and table_content.get("table_data"):
        table_type = "meter"
    else:
        for i, row in enumerate(table_content['table_data']):
            stripped_values = [value.strip() for value in row.values()]
            if any(x in stripped_values for x in ['water', 'sewer', 'grease']):
                table_type = "charges"
    return table_type

def retrieve_entities(base_location):
    table_data_boxes = []
    table_data = []
    column_bounds = []
    if 'table_data_boxes' in base_location:
        table_data_boxes = base_location['table_data_boxes']
    if 'table_data' in base_location:
        table_data = base_location['table_data']
    if 'column_bounds' in base_location:
        column_bounds = base_location['column_bounds']
    return table_data_boxes, table_data, column_bounds


def update_charges_table_data(table_data):
    idx_to_remove = []
    for idx,data in enumerate(table_data):
        striped_values = [value.strip() for value in data.values()]
        if any(x in striped_values[0].lower() for x in ['description', 'amount', 'balance forward', 'payment']):
            idx_to_remove.append(idx)
    table_data = [j for i, j in enumerate(table_data) if i not in idx_to_remove]
    for idx, data in enumerate(table_data):
        striped_values = [value.strip() for value in data.values()]
        if any(x in striped_values[0].lower() for x in
               ['water', 'nhcrwa fee', 'consumption', 'tceq', 'lsgwc', 'sjra', 'rwa fee', 'wtr swr svc fee',
                'surface water', 'grp fee', 'whcrwa fee', 'nfbwa usage fee', 'reg assmt fee', 'security fee', 'wasw',
                'lsgcd']):
            serviceType = "Water"
            subServiceType = "Water"
        elif any(x in striped_values[0].lower() for x in
                 ['mtr chg 1"', 'sewer', 'incust surcharg', 'grease', 'grease trap']):
            serviceType = "Water"
            subServiceType = "Sewer"
        elif any(x in striped_values[0].lower() for x in
                 ['basic service', 'gas delivery', 'cost of gas', 'coga 0.5743', 'service rate', 'franchise fee']):
            serviceType = "Natural gas"
            subServiceType = "Natural gas"
        elif any(x in striped_values[0].lower() for x in ['stormwater fee-com']):
            serviceType = "Water"
            subServiceType = "Drainage"
        elif any(x in striped_values[0].lower() for x in ['irrigation']):
            serviceType = "Water"
            subServiceType = "Irrigation"
        else:
            serviceType = ""
            subServiceType = ""
        data['2'] = serviceType
        data['3'] = subServiceType

    table_data.insert(0, {'0': 'c2des',  # charges_description_corpus_cristi
                                               '1': 'c2cost',  # charges cost_corpus_cristi
                                               '2': 'c2Serv',  # charges ServiceType_corpus_cristi
                                               '3': 'c2subS'})  # charges subServiceType_corpus_cristi
    return table_data

def divide_column_bounds(column_bounds, n_columns):
    divided_column_bounds = []
    if column_bounds:
        table_width = column_bounds[-1]['x2'] - column_bounds[0]['x1']
        table_x1 = column_bounds[0]['x1']
        table_y1 = column_bounds[0]['y1']
        table_y2 = column_bounds[0]['y2']
        for column in range(n_columns):
            divided_column_bounds.append({
                'y1': int(table_y1),
                'x1': int(table_x1 + (table_width / n_columns) * column),
                'y2': int(table_y2),
                'x2': int(table_x1 + (table_width / n_columns) * (column + 1))
            })
    return divided_column_bounds

def write_json(base_location, table_data_boxes, table_data, column_bounds):
    base_location['table_data_boxes'] = table_data_boxes
    base_location['table_data'] = table_data
    base_location['column_bounds'] = column_bounds
    return base_location

def update_meter_table_data(table_data,smartextract_jsons):
    idx_to_remove = []
    for idx, row in enumerate(table_data):
        striped_values = [value.strip() for value in row.values()]
        if any(x in striped_values[0].lower() for x in ['number', 'reading', 'used', 'day ', 'current', 'meter', 'previous', 'gallons', 'current reading',
                                                        'meter number', 'previous reading', 'gallons used']):
            idx_to_remove.append(idx)
    table_data = [j for i, j in enumerate(table_data) if i not in idx_to_remove]

    for idx, data in enumerate(table_data):
        striped_values = [value.strip() for value in data.values()]
        if any(x in striped_values for x in ['w-gls','w','water', 'nhcrwa fee', 'consumption', 'tceq', 'lsgwc', 'sjra', 'rwa fee', 'wtr swr svc fee',
                                                        'surface water', 'grp fee', 'whcrwa fee', 'nfbwa usage fee', 'reg assmt fee', 'security fee', 'wasw','lsgcd']):
            serviceType = "Water"
            subServiceType = "Water"
        elif any(x in striped_values for x in ['mtr chg 1"', 'sewer', 'incust surcharg', 'grease', 'grease trap']):
            serviceType = "Water"
            subServiceType = "Sewer"
        elif any(x in striped_values for x in ['basic service', 'gas delivery', 'cost of gas', 'coga 0.5743', 'service rate', 'franchise fee']):
            serviceType = "Natural gas"
            subServiceType = "Natural gas"
        elif any(x in striped_values for x in ['stormwater fee-com']):
            serviceType = "Water"
            subServiceType = "Drainage"
        elif any(x in striped_values for x in ['irrigation']):
            serviceType = "Water"
            subServiceType = "Irrigation"
        else:
            serviceType = ""
            subServiceType = ""
        meter_number = data.get('0')
        previous_reading = data.get('1')
        current_reading = data.get('2')
        usage = data.get('3')
        uom = 'kGal'
        meterMultiplier = ''
        powerFactor = ''
        demandUsage = ''
        #call retrive_fois function to get service start/end date
        fields = retrieve_foi_entities(smartextract_jsons[0])
        if 'from_date' in fields:
            servicePeriodStartDate = fields['to_date'][0]
        else:
            servicePeriodStartDate = ""
        if 'to_date' in fields:
            servicePeriodEndDate = fields['to_date'][0]
        else:
            servicePeriodEndDate = " "

        #assign extrcated values to the table_data and rearrange their positions
        data['0'] = serviceType
        data['1'] = meter_number
        data['2'] = previous_reading
        data['3'] = current_reading
        data['4'] = usage
        data['5'] = servicePeriodEndDate
        data['6'] = servicePeriodStartDate
        data['7'] = subServiceType
        data['8'] = uom
        data['9'] = meterMultiplier
        data['10'] = powerFactor
        data['11'] = demandUsage
    # adding heder to a table
    header_row = {}
    header_row["0"] = "c2mst"  # serviceType
    header_row["1"] = "c2mN"  # meterNumber
    header_row["2"] = "c2mRP"  # meterReadPrevious
    header_row["3"] = "c2mRC"  # meterReadCurrent
    header_row["4"] = "c2ubm"  # usageByMeter
    header_row["5"] = "c2sped"  # servicePeriodEndDate
    header_row["6"] = "c2spsd"  # servicePeriodStartDate
    header_row["7"] = "c2msst"  # subServiceType
    header_row["8"] = "c2uom"  # uom
    header_row["9"] = "c2mm"  # meterMultiplier
    header_row["10"] = "c2pf"  # powerFactor
    header_row["11"] = "c2du"  # demandUsage'''

    table_data.insert(0, header_row)
    return table_data


def retrieve_foi_entities(data):
    base_location = (data['hits']['hits'][0]['_source']['data'])
    field_names = ['meter_number', 'current_reading', 'previous_reading', 'usage', 'service_type', 'subservice_type', 'from_date','to_date']
    fields = {}
    for d in base_location:
        if d['field'] in field_names:
            fields[d['field']] = []
            for answer in d['answer']:
                fields[d['field']].append(answer['text'])
    return fields


def create_table_data(fields, table_fields):
    table_data = []
    # Add headers
    data = {}
    i = 0
    for i, item in enumerate(table_fields):
        data[str(i)] = item
    table_data.append(data)

    # Add data
    data = {}
    data['0'] = ''.join(fields['current_reading'])
    data['1'] = ''.join(fields['meter_number'])
    data['2'] = ''.join(fields['previous_reading'])
    data['3'] = ''.join(fields['service_type'])
    data['4'] = ''.join(fields['subservice_type'])
    data['5'] = ''.join(fields['usage'])
    data['6'] = ''.join(fields['to_date'])
    data['7'] = ''.join(fields['from_date'])
    data['8'] = 'kGal'
    data['9'] = ''
    data['10'] = ''
    data['11'] = ''

    table_data.append(data)
    return table_data

def create_meter_table_from_foi(input_tables_data,table_data):
    meter_table_structure = {}
    for table_id, table_content in input_tables_data.items():
        if get_table_type(table_content) == "charges":
            original_meter_column_bounds = table_content['column_bounds']
            column_bounds = divide_column_bounds(original_meter_column_bounds, 12)
            meter_table_structure["row_merging_type"] = table_content["row_merging_type"]
            meter_table_structure["post_remove_less_populated_lines"] = table_content["post_remove_less_populated_lines"]
            meter_table_structure["column_mappings"] = {}
            meter_table_structure["accuracy"] = table_content["accuracy"]
            meter_table_structure["document_id"] = table_content["document_id"]
            meter_table_structure["predictions"] = []
            meter_table_structure["execution_time"] = table_content["execution_time"]
            meter_table_structure["document_name"] = table_content["document_name"]
            meter_table_structure["post_skip_lines_keywords"] = table_content["post_skip_lines_keywords"]
            meter_table_structure["width"] = table_content["width"]
            meter_table_structure["folder_index"] = table_content["folder_index"]
            meter_table_structure["raw_table_data_boxes"] = []
            meter_table_structure["ocr_line_coords"] = []
            meter_table_structure["height"] = table_content["height"]
            meter_table_structure["character_count"] = table_content["character_count"]
            meter_table_structure['table_data'] = table_data
            meter_table_structure['table_data_boxes'] = []
            meter_table_structure['table_identified'] = "meter"
            meter_table_structure['column_bounds'] = column_bounds
            # updated_meter_table[table_id_new] = new_table_structure
    return meter_table_structure
def run(input_tables_data, smartextract_jsons):
    charges_table_found = False
    meter_table_found =  False
    updated_table_json = {}
    for table_id, table_content in input_tables_data.items():
        if get_table_type(table_content) == "charges":
            table_data_boxes, table_data, original_charges_column_bounds = retrieve_entities(table_content)
            table_data_boxes = []
            table_data = update_charges_table_data(table_data)
            column_bounds = divide_column_bounds(original_charges_column_bounds, 4)
            table_content = write_json(table_content, table_data_boxes, table_data, column_bounds)
            charges_table_found = True
            updated_table_json[table_id] = table_content
        if get_table_type(table_content) == "meter":
            table_data_boxes, table_data, original_meter_column_bounds = retrieve_entities(table_content)
            table_data_boxes = []
            table_data = update_meter_table_data(table_data,smartextract_jsons)
            column_bounds = divide_column_bounds(original_meter_column_bounds, 12)
            table_content = write_json(table_content, table_data_boxes, table_data, column_bounds)
            meter_table_found = True
            updated_table_json[table_id] = table_content
    if not meter_table_found:
        fields = retrieve_foi_entities(smartextract_jsons[0])
        table_fields = ["c2mRC",  # meterReadCurrent,
                        "c2mN",  # "meterNumber",
                        "c2mRP",  # "meterReadPrevious",
                        "c2mst",  # serviceType
                        "c2msst",  # subServiceType
                        "c2ubm",  # "usageByMeter",
                        "c2sped",  # servicePeriodEndDateusageByMeter",
                        "c2spsd",  # servicePeriodStartDate
                        "c2uom",  # uom
                        "c2mm",  # meterMultiplier
                        "c2pf",  # powerFactor
                        "c2du"]  # demandUsage
        table_data = create_table_data(fields, table_fields)
        meter_table_structure = create_meter_table_from_foi(input_tables_data,table_data)
        new_meter_table_id = uuid.uuid1().hex
        updated_table_json[new_meter_table_id] = meter_table_structure
        updated_table_json = json.dumps(updated_table_json)

    print(updated_table_json)

    # Only for testing - Remove this later
if __name__=='__main__':
    # table_file = "Tables/304050455504301.json"
    # table_file = r'/home/u65480/Downloads/category2/json/table/cat2_24037500.json'
    table_file = r'/home/u65480/Downloads/category2/json/table/cat2_304050455504301.json'

    # foi_file = "FOI/304050455504301.json"
    # foi_file = r'/home/u65480/Downloads/category2/json/foi/cat2_24037500.json'
    foi_file = r'/home/u65480/Downloads/category2/json/foi/cat2_304050455504301.json'

    with open(table_file) as fp:
        input_tables_data = json.load(fp)
    with open(foi_file) as ffp:
        smartextract_jsons = json.load(ffp)
    run(input_tables_data, smartextract_jsons)
