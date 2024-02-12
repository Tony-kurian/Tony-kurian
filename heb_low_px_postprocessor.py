import re
import json

service_type_mapping = {
    'Water': 'Water',
    'Sewer': 'Water',
    'Brush': 'Water',
    'Chamber': 'Water',
    'Electric': 'Electric',
    'Fire Dept': 'Water',
    'Fire Fee': 'Water',
    'Garbage': 'Garbage',
    'Miscellaneous': 'Water',
    'Night Light': 'Electric',
    'Tax': 'Water',
    'Drainage': 'Water',
    'Capital Imp': 'Water',
    'Fire': 'Water',
    'Reconnect Fee': 'Water',
    'Sprinkler': 'Water',
    'Drainage Fee': 'Water',
    'Fire Prot.': 'Water',
    'Sewer Dep': 'Water',
    'TCEQ Fee': 'Water',
    'Street': 'Street'
}

uom_mapping = {
    'Water': 'Gal',
    'Electric': 'kWh',
    'Garbage': 'Gal',
    'Street': 'kWh'  # not sure about it considering street lights its kWh
}

sub_service_type_mapping = {
    'SE': 'Sewer',  # City of Mission. City of Mercedes
    'WA': 'Water',  # City of Mission. City of Mercedes. City of Kennedy. City of Weslaco. City of San Benito.
    'SW': 'Sewer',  # City of Kennedy. City of Harlingen Waterworks. City of Weslaco. City of San Benito.
    'DR': 'Drainage',  # City of Mission
    'FF': 'Water',  # City of Mercedes
    'BR': 'Brush',  # City of Mercedes
    'TX SALES': 'Brush',  # City of Mercedes
    'TX STATE': 'Brush',  # City of Mercedes
    'GA': 'Garbage',  # City of Mission. City of Mercedes. City of Weslaco
    'PD': 'Water',  # City of Mercedes
    'BP': 'Brush',  # City of Mercedes
    'BA': 'Water',  # City of Mission
    'SC': 'Water',  # City of Mission
    'SP': 'Irrigation',  # City of Mission
    'WT': 'Water',  # City of Harlingen Waterworks.
    'RF': 'Garbage',  # City of Harlingen Waterworks
    'TX': 'Garbage',  # City of Harlingen Waterworks. City of San Benito
    'SM': 'Street',  # City of Harlingen Waterworks
    'FL': 'Water',  # City of Harlingen Waterworks
    'CI': 'Water',  # City of Weslaco
    'TAX': 'Garbage',  # City of Weslaco
    'GT': 'Sewer',  # City of Weslaco
    'AR': 'Water',  # City of Weslaco
    'AF': 'Water',  # City of Weslaco
    'MI': 'Water',  # City of Weslaco
    'BF': 'Brush',  # City of Weslaco
    'ST': 'Drainage',  # City of San Benito
    'GB': 'Garbage',  # City of San Benito
    'OV': 'Garbage',  # City of San Benito
    'EX': 'Garbage',  # City of Sinton
    'SANITATION': 'Garbage',  # City of Crystal City
    'MF': 'Water',
    'LS': 'Water',
    'SJ': 'Water',
    'FRA': 'Water',
    'BOND': 'Water',
    'WAT2': 'Water',
    'LC': 'Water',
    'OTHER': 'Water',
    'WATER': 'Water',
    'SEWER': 'Sewer',
    'SEWAGE': 'Sewer',  # City of La Vernia
    'GARBAGE': 'Garbage',  # City of La Vernia
    'SALES TAX': 'Garbage',  # City of La Vernia
    'LATE CHARGE': 'Water',  # City of La Vernia
    'PAST DUE': 'Water',  # City of La Vernia
    'OM CHARGE': 'Water',  # City of La Vernia
    'REGULATORY FEE'
    'TCEQ FEE': 'Water',
    'CC': 'Chamber',
    'EL': 'Electric',
    'FD': 'Water',
    'MISC': 'Miscellaneous',
    'NL': 'Night Light',
    'GAR': 'Garbage',
    'FI': 'Water',
    'RC': 'Reconnect Fee',
    'DF': 'Drainage',
    'FP': 'Water.',
    'SD': 'Sewer',
    'WAT': 'Water',
    'SEW': 'Sewer',
    'FIRE': 'Water',
    'BRUSH': 'Brush'
}

keywords = {
    'amount': ['amount', 'charges'],
    'description': ['code', 'service', 'gode', 'detail'],
    'usageByMeter': ['usage', 'consumption', 'gallons used', 'used'],
    'meterReadCurrent': ['present', 'current'],
    'meterReadPrevious': ['previous']
}


def get_table_content(input_tables, table_with_content):
    extracted_columns = {}
    column_mapping = []
    for doc_id, input_table in input_tables.items():
        if input_table['table_identified'].lower() == table_with_content:
            # Map columns
            column_mapping = {
                'amount': '',
                'description': '',
                'usageByMeter': '',
                'meterReadCurrent': '',
                'meterReadPrevious': ''
            }
            first_row = None
            for i, row in enumerate(input_table.get('table_data', [])):
                for column, cell in row.items():
                    if (first_row is None and (re.findall('[0-9]', row.get(column_mapping['usageByMeter'], '')) or
                                               (re.findall('[0-9]', cell) and row.get(column_mapping['description'],
                                                                                      '').strip()))):  # get first row with numbers and code or with usageByMeter
                        first_row = i
                    for line_item_field, search_keywords in keywords.items():
                        if column not in column_mapping.values() and not column_mapping[line_item_field]:
                            for keyword in search_keywords:
                                if keyword in cell.lower().strip():
                                    column_mapping[line_item_field] = column
            if first_row is None:
                first_row = 0

            # Get content
            for column_name, column in column_mapping.items():
                if column:
                    extracted_columns[column_name] = [row[column_mapping[column_name]] for row in
                                                      input_table['table_data_boxes'][first_row:]]
                else:
                    if 'table_data_boxes' in input_table:
                        extracted_columns[column_name] = [[] for _ in input_table['table_data_boxes'][first_row:]]
                    else:
                        extracted_columns[column_name] = []

    return extracted_columns, column_mapping


def get_sub_service_type(description_row):
    code = re.sub('[^A-z]', '', ''.join([word['word'] for word in description_row]).upper())
    if code in sub_service_type_mapping:
        return sub_service_type_mapping[code]
    for word in description_row:
        if word['word'] in sub_service_type_mapping:
            return sub_service_type_mapping[word['word']]
    return ''


def get_custom_table_columns(extracted_columns):
    extracted_columns['meterReadCurrent'] += [[]] * (
                len(extracted_columns['usageByMeter']) - len(extracted_columns['meterReadCurrent']))
    extracted_columns['meterReadPrevious'] += [[]] * (
                len(extracted_columns['usageByMeter']) - len(extracted_columns['meterReadPrevious']))

    extracted_columns['subServiceType'] = [[{'word': get_sub_service_type(description_row),
                                             'ocr_score': description_row[0]['ocr_score'],
                                             'coords': description_row[0]['coords']}] if description_row else []
                                           for description_row in extracted_columns['description']]
    extracted_columns['serviceType'] = [[{'word': service_type_mapping.get(subservice_row[0]['word'], ''),
                                          'ocr_score': subservice_row[0]['ocr_score'],
                                          'coords': subservice_row[0]['coords']}] if subservice_row else []
                                        for subservice_row in extracted_columns['subServiceType']]
    extracted_columns['uom'] = [[{'word': uom_mapping.get(service_row[0]['word'], ''),
                                  'ocr_score': service_row[0]['ocr_score'],
                                  'coords': service_row[0]['coords']}] if service_row else []
                                for service_row in extracted_columns['serviceType']]
    return extracted_columns


def get_columns_from_fois(input_fois, extracted_columns):
    extracted_columns['servicePeriodStartDate'] = [[]] * len(extracted_columns['usageByMeter'])
    extracted_columns['servicePeriodEndDate'] = [[]] * len(extracted_columns['usageByMeter'])
    for fois_page in input_fois:
        for foi_extracted in fois_page['hits']['hits'][0]['_source']['data']:
            if foi_extracted['field'] == 'from_date' and foi_extracted['candidates'][0]['answer'][0]['text'] != 'NA':
                text = ' '.join([word['text'] for word in foi_extracted['candidates'][0]['answer']])
                extracted_columns['servicePeriodStartDate'] = [[{'word': text,
                                                                 'ocr_score':
                                                                     foi_extracted['candidates'][0]['answer'][0][
                                                                         'ocr_score'],
                                                                 'coords': {
                                                                     "y1": foi_extracted['candidates'][0]['answer'][0][
                                                                         'box']['Y'],
                                                                     "x1": foi_extracted['candidates'][0]['answer'][0][
                                                                         'box']['X'],
                                                                     "y2": foi_extracted['candidates'][0]['answer'][0][
                                                                               'box']['Y'] +
                                                                           foi_extracted['candidates'][0]['answer'][0][
                                                                               'box']['H'],
                                                                     "x2": foi_extracted['candidates'][0]['answer'][0][
                                                                               'box']['X'] +
                                                                           foi_extracted['candidates'][0]['answer'][0][
                                                                               'box']['W']
                                                                 }}]] * len(extracted_columns['usageByMeter'])
            elif foi_extracted['field'] == 'to_date' and foi_extracted['candidates'][0]['answer'][0]['text'] != 'NA':
                text = ' '.join([word['text'] for word in foi_extracted['candidates'][0]['answer']])
                extracted_columns['servicePeriodEndDate'] = [[{'word': text,
                                                               'ocr_score': foi_extracted['candidates'][0]['answer'][0][
                                                                   'ocr_score'],
                                                               'coords': {
                                                                   "y1": foi_extracted['candidates'][0]['answer'][0][
                                                                       'box']['Y'],
                                                                   "x1": foi_extracted['candidates'][0]['answer'][0][
                                                                       'box']['X'],
                                                                   "y2": foi_extracted['candidates'][0]['answer'][0][
                                                                             'box']['Y'] +
                                                                         foi_extracted['candidates'][0]['answer'][0][
                                                                             'box']['H'],
                                                                   "x2": foi_extracted['candidates'][0]['answer'][0][
                                                                             'box']['X'] +
                                                                         foi_extracted['candidates'][0]['answer'][0][
                                                                             'box']['W']
                                                               }}]] * len(extracted_columns['usageByMeter'])
    return extracted_columns


def table_box_to_foi_structure(table_boxes):
    return [{"score": 0.99,
             "ocr_score": table_box['ocr_score'],
             "box": {"X": table_box['coords']['x1'],
                     "Y": table_box['coords']['y1'],
                     "H": table_box['coords']['y2'] - table_box['coords']['y1'],
                     "W": table_box['coords']['x2'] - table_box['coords']['x1']},
             "text": table_box['word']
             } for table_box in table_boxes]


def set_fois_from_table(input_fois, input_tables, column_mapping, table_with_content):
    late_fee = []
    carry_forward_balance = []
    late_fee_keywords = ['late']
    carry_forward_balance_keywords = ['past due', 'credit', 'arrears']
    for doc_id, input_table in input_tables.items():
        if input_table['table_identified'].lower() == table_with_content:
            for i, row in enumerate(input_table.get('table_data', [])):
                if 'amount' in column_mapping and re.findall('[0-9]', row.get(column_mapping['amount'], '')):
                    if any(keyword in ' '.join(row.values()).lower() for keyword in carry_forward_balance_keywords):
                        carry_forward_balance_boxes = input_table['table_data_boxes'][i][column_mapping['amount']]
                        carry_forward_balance = table_box_to_foi_structure(carry_forward_balance_boxes)
                    elif any(keyword in ' '.join(row.values()).lower() for keyword in late_fee_keywords):
                        late_fee_boxes = input_table['table_data_boxes'][i][column_mapping['amount']]
                        late_fee = table_box_to_foi_structure(late_fee_boxes)

    for foi_extracted in input_fois[0]['hits']['hits'][0]['_source']['data']:
        if foi_extracted['field'] == 'lateFee' and late_fee:
            values_to_update = {"answer": late_fee, "manswer": late_fee, "ranswer": late_fee}
            foi_extracted.update(values_to_update.copy())
            foi_extracted['candidates'][0].update(values_to_update.copy())
            foi_extracted['candidates'][0]['score'] = 99.9
        elif foi_extracted['field'] == 'carry_forward_balance' and carry_forward_balance:
            values_to_update = {"answer": carry_forward_balance, "manswer": carry_forward_balance,
                                "ranswer": carry_forward_balance}
            foi_extracted.update(values_to_update.copy())
            foi_extracted['candidates'][0].update(values_to_update.copy())
            foi_extracted['candidates'][0]['score'] = 99.9

    return input_fois


def get_charges_table_data_boxes(extracted_columns):
    charges_table_data_boxes = [
        {
            "0": [{"ocr_score": 1.0,
                   "word": "lowpxserviceType",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "1": [{"ocr_score": 1.0,
                   "word": "lowpxsubServiceType",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "2": [{"ocr_score": 1.0,
                   "word": "lowpxdescription",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "3": [{"ocr_score": 1.0,
                   "word": "lowpxamount",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
        }]

    for service_row, subservice_row, description_row, amount_row in zip(extracted_columns['serviceType'],
                                                                        extracted_columns['subServiceType'],
                                                                        extracted_columns['description'],
                                                                        extracted_columns['amount']):
        if any([service_row, subservice_row, description_row, amount_row]):
            charges_table_data_boxes.append({
                "0": service_row,
                "1": subservice_row,
                "2": description_row,
                "3": amount_row
            })
    return charges_table_data_boxes


def delete_alphabetical_characters(cell):
    for word in cell:
        word['word'] = re.sub('[^0-9.,]', '', word['word'])
    return cell


def get_meter_table_data_boxes(extracted_columns):
    meter_table_data_boxes = [
        {
            "0": [{"ocr_score": 1.0,
                   "word": "lowpxserviceType",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "1": [{"ocr_score": 1.0,
                   "word": "lowpxsubServiceType",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "2": [{"ocr_score": 1.0,
                   "word": "lowpxservicePeriodStartDate",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "3": [{"ocr_score": 1.0,
                   "word": "lowpxservicePeriodEndDate",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "4": [{"ocr_score": 1.0,
                   "word": "lowpxmeterNumber",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "5": [{"ocr_score": 1.0,
                   "word": "lowpxmeterReadPrevious",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "6": [{"ocr_score": 1.0,
                   "word": "lowpxmeterReadCurrent",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "7": [{"ocr_score": 1.0,
                   "word": "lowpxuom",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "8": [{"ocr_score": 1.0,
                   "word": "lowpxusageByMeter",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "9": [{"ocr_score": 1.0,
                   "word": "lowpxmeterMultiplier",
                   "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "10": [{"ocr_score": 1.0,
                    "word": "lowpxpowerFactor",
                    "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}],
            "11": [{"ocr_score": 1.0,
                    "word": "lowpxdemandUsage",
                    "coords": {"y1": 0, "x1": 0, "y2": 0, "x2": 0}}]

        }]

    for i, (service_row, subservice_row, service_period_start_row, service_period_end_row,
            meter_read_previous_row, meter_read_current_row, uom_row, usage_row) in enumerate(
        zip(extracted_columns['serviceType'], extracted_columns['subServiceType'],
            extracted_columns['servicePeriodStartDate'], extracted_columns['servicePeriodEndDate'],
            extracted_columns['meterReadPrevious'], extracted_columns['meterReadCurrent'],
            extracted_columns['uom'], extracted_columns['usageByMeter'])):
        if not (usage_row and delete_alphabetical_characters(usage_row)[0]['word'] == "0" and not subservice_row) and \
                ((usage_row and delete_alphabetical_characters(usage_row)[0]['word']) or
                 (meter_read_previous_row and delete_alphabetical_characters(meter_read_previous_row)[0]['word']) or
                 (meter_read_current_row and delete_alphabetical_characters(meter_read_current_row)[0]['word']) or
                 (i == 0 and (service_period_start_row or service_period_end_row))):
            meter_table_data_boxes.append({
                "0": service_row,
                "1": subservice_row,
                "2": service_period_start_row,
                "3": service_period_end_row,
                "4": [],
                "5": delete_alphabetical_characters(meter_read_previous_row),
                "6": delete_alphabetical_characters(meter_read_current_row),
                "7": uom_row,
                "8": delete_alphabetical_characters(usage_row),
                "9": [],
                "10": [],
                "11": []
            })
    return meter_table_data_boxes


def get_table_data_from_table_data_boxes(table_data_boxes):
    table_data = []
    for row in table_data_boxes:
        table_data.append({i: ' '.join([word['word'] for word in content]) for i, content in row.items()})

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


def get_table_name_with_content(input_tables):
    for doc_id, input_table in input_tables.items():
        if "table_data" in input_table:
            return input_table['table_identified'].lower()
    return "charges_table"


def run(doc_ids, input_ocr, input_tables, input_fois):
    print('Starting postprocessor HEB Low Pixel')
    print('Tables: ', input_tables)
    print('FOIs: ', input_fois)
    charges_table = {}
    meter_table = {}
    table_with_content = get_table_name_with_content(input_tables)

    extracted_columns, column_mapping = get_table_content(input_tables, table_with_content)
    extracted_columns = get_custom_table_columns(extracted_columns)
    extracted_columns = get_columns_from_fois(input_fois, extracted_columns)
    print('Extracted columns: ', extracted_columns)

    input_fois = set_fois_from_table(input_fois, input_tables, column_mapping, table_with_content)

    charges_table['table_data_boxes'] = get_charges_table_data_boxes(extracted_columns)
    meter_table['table_data_boxes'] = get_meter_table_data_boxes(extracted_columns)
    charges_table['table_data'] = get_table_data_from_table_data_boxes(charges_table['table_data_boxes'])
    meter_table['table_data'] = get_table_data_from_table_data_boxes(meter_table['table_data_boxes'])
    charges_table['accuracy'] = 99.99  # mandatory field
    meter_table['accuracy'] = 99.99  # mandatory field

    # column bounds
    for doc_id, input_table in input_tables.items():
        if input_table['table_identified'].lower() == table_with_content:
            charges_table['column_bounds'] = divide_column_bounds(input_table.get('column_bounds', []), 4)
            meter_table['column_bounds'] = divide_column_bounds(input_table.get('column_bounds', []), 12)

    # update dict
    for doc_id, input_table in input_tables.items():
        if input_table['table_identified'].lower() == 'charges_table':
            input_table.update(charges_table)
        elif input_table['table_identified'].lower() == 'meter_table':
            input_table.update(meter_table)
    print('Postprocessor HEB Low Pixel completed')
    print('Tables: ', input_tables)
    print('FOIs: ', input_fois)
    return input_tables, input_fois
