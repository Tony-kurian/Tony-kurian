import json   
import re

def divide_column_bounds(column_bounds, n_columns):
    divided_column_bounds = []
    if column_bounds:
        table_width =  column_bounds[-1]['x2'] - column_bounds[0]['x1']
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

def reindex_table_data_boxes(table_data_boxes):

    for row in table_data_boxes:
        fields_to_add = ["saServ","sasubS"]
        for idx, field in enumerate(fields_to_add):
            row[str(2+idx)]=[{"ocr_score":0.9,"word":field,"coords":{'y1': 0, 'x1': 0, 'y2': 0, 'x2': 0}}]

    return table_data_boxes

def update_table_data(table_data):
    for data in table_data:
        # data['2'] = data.pop('0')
        # data['3'] = data.pop('1')
        data['2'] = 'Water'
        cleaned_text =re.sub("[^A-Za-z ]","",data['0']).lower()
        sub_service = 'Water'
        if any(x in cleaned_text for x in ['sewer', 'fats', 'oils', 'grease']):
            sub_service = 'Sewer'
        elif any(x in cleaned_text for x in ['stormwater', 'storm water']):
            sub_service = 'Drainage'
        elif 'irrigation' in cleaned_text:
            sub_service = 'Irrigation'
        data['3'] = sub_service
    data = {}
    data["0"] = "sades"
    data["1"] = "sacost"
    data["2"] = "saServ"
    data["3"] = "sasubS"
    
    table_data.insert(0, data)
    return table_data


def write_json(base_location, table_data_boxes, table_data, column_bounds):
    base_location['table_data_boxes'] = table_data_boxes
    base_location['table_data'] = table_data
    base_location['column_bounds'] = column_bounds
    return base_location
  
def retrieve_foi_entities(data):
    base_location = (data['hits']['hits'][0]['_source']['data'])
    field_names = ['multiplier', 'reading', 'from_date', 'to_date', 'water_usage']
    fields = {}
    for d in base_location:
        if d['field'] in field_names:
            if d['field'] == 'reading':
                fields['prev_reading'] = []
                fields['current_reading'] = []
                #Perform validations and null check
                if not 'answer' in d:
                    continue
                if len(d['answer']) == 0:
                    continue
                
                answer_text = ""
                for answer in d['answer']:
                    if not 'text' in answer:
                        continue
                    answer_text += answer['text']
                if '-' in answer_text:
                    #Calculate meter reading start and end 
                    meter_start_end = answer_text.split('-')
                    meter_end = meter_start_end[0]
                    if '=' in meter_start_end[1]:
                        meter_start = meter_start_end[1].split('=')[0]
                    else:
                        meter_start = meter_start_end[1]

                    #Add start to meter reading separately
                    fields['prev_reading'].append(meter_start)
                    
                    #Add end to meter reading separately
                    fields['current_reading'].append(meter_end)
            elif d['field'] == 'multiplier':
                fields[d['field']] = []
                #Perform validations and null check
                if not 'answer' in d:
                    continue
                if len(d['answer']) == 0:
                    continue
                answer_text = ""
                for answer in d['answer']:
                    if not 'text' in answer:
                        continue
                    answer_text += answer['text']
                multiplier = answer_text.lower().split('x')
                multiplier_clean=""
                for cand in multiplier:
                    if "=" in cand :
                        multiplier_clean = cand.split('=')[0]
                        break
                    else:
                        multiplier_clean = cand

                fields[d['field']].append(multiplier_clean)
            else:
                fields[d['field']] = []
                for answer in d['answer']: 
                    fields[d['field']].append(answer['text'])
    return fields


def create_table_data(fields, table_fields):
    table_data = []
    #Add headers
    data = {}
    i = 0
    for i, item in enumerate(table_fields):
        data[str(i)] = item
    table_data.append(data)
    
    #Add data
    data = {}
    data['0'] = ''.join(fields['current_reading'])
    data['1'] = ''
    data['2'] = ''.join(fields['prev_reading'])
    data['3'] = 'Water' #
    data['4'] = 'Water'
    data['5'] = ''.join(fields['water_usage'])
    data['6'] = ' '.join(fields['to_date'])
    data['7'] = ' '.join(fields['from_date'])
    data['8'] = 'Gal'
    data['9'] = fields['multiplier'][0]
    data['10']=''
    data['11']=''
    
    table_data.append(data)
    return table_data

def create_table_json(table_data):
    table_json = {}
    table_json['table_data'] = table_data
    table_json['table_data_boxes'] = []
    table_json['column_bounds'] = []
    return table_json

def run(docs, input_ocr_data, input_tables_data, smartextract_jsons):
    file_path = '/tmp/input_tables_data.json'
    with open(file_path, 'w') as file:
        file.write(str(input_tables_data))

    file_path = '/tmp/input_ocr_data.json'
    with open(file_path, 'w') as file:
        file.write(str(input_ocr_data))

    file_path = '/tmp/docs.json'
    with open(file_path, 'w') as file:
        file.write(str(docs))

    file_path = '/tmp/smartextract_jsons.json'
    with open(file_path, 'w') as file:
        file.write(str(smartextract_jsons))

    already_meter_extracted=False
    original_charges_column_bounds = []
    for table_id, table_content in input_tables_data.items():
        if table_content.get("table_identified") == "charges_table" and table_content.get("table_data"):
            table_data_boxes, table_data, original_charges_column_bounds = retrieve_entities(table_content)
            table_data_boxes = []
            table_data = update_table_data(table_data)
            column_bounds = divide_column_bounds(original_charges_column_bounds, 4)
            table_content = write_json(table_content, table_data_boxes, table_data, column_bounds)
            
        if table_content.get("table_identified") == "meter_table" and not already_meter_extracted:
            already_meter_extracted=True
            table_content["accuracy"]=99.94
            table_content["accuracy"]=249
            table_content["document_id"]=docs[0]
            table_content["document_name"]="xxx"
            table_content["execution_time"]=0.00
            table_content["folder_index"]=0
            table_content["height"]=2200
            fields = retrieve_foi_entities(smartextract_jsons[1])
            
            table_fields = ["samRC", #meterReadCurrent,
                            "samN", #"meterNumber", 
                            "samRP", #"meterReadPrevious", 
                            "samst", #serviceType
                            "samsst", #subServiceType
                            "saubm", #"usageByMeter", 
                            "sasped", #servicePeriodEndDateusageByMeter", 
                            "saspsd", #servicePeriodStartDate
                            "sauom", #uom
                            "samm",#meterMultiplier
                            "sapf",#powerFactor
                            "sadu"]#demandUsage
            
            table_data = create_table_data(fields, table_fields)
            table_content['table_data'] = table_data
            table_content['table_data_boxes'] = []

    for table_id, table_content in input_tables_data.items():
        if table_content.get("table_identified") == "meter_table":
            table_content['column_bounds'] = divide_column_bounds(original_charges_column_bounds, 12)
    
    return input_tables_data, smartextract_jsons
            