import json 

mapping_service = {"WATER COMM":"Water",
                   "IRRIGATION":"Water",
                   "SEWER INDSWRSUR": "Water",
                   "WATER INDSWRSUR": "Water"}

mapping_sub_service = {"WATER COMM":"Water",
                       "IRRIGATION":"Irrigation",
                       "SEWER INDSWRSUR": "Water",
                       "WATER INDSWRSUR": "Sewer"}

mapping_uom = "kGal"'''{"WATER COMM":"kGal",
               "IRRIGATION":"kGal"}'''


def run(docs, input_ocr_data, input_tables_data,smartextract_jsons):
        
    print("==========houston============")
    for table_id, table_content in input_tables_data.items():
    
        if 'page_1' in table_content['document_name']:
            
            
            table_content['table_data_boxes'] = []
            table_content['table_data'] = []
            table_content['column_bounds'] = []
            table_content['table_identified'] = 'unrecognized'
        else:
            if table_content.get("table_identified") == "meter_table" and table_content.get("table_data"):
                #meter table
                
                last_value = table_content["column_bounds"][-1]
                
                for i in range(6):
                    new_value = {
                        'y1': last_value['y1'],
                        'x1': last_value['x2'] + (i * 10),
                        'y2': last_value['y2'],
                        'x2': last_value['x2'] + ((i + 1) * 10)
                    }
                                        
                    table_content["column_bounds"].extend([new_value])

                
                for row in table_content["table_data_boxes"]:
                    fields_to_add = ["ccspsd","ccmsst","ccuom","ccmm","ccpf","ccdu"]
                    available_columns = 7
                    for idx, field in enumerate(fields_to_add):
                        row[available_columns+idx]=[{"ocr_score":0.9,"word":field,"coords":{'y1': 0, 'x1': 0, 'y2': 0, 'x2': 0}}]
                    
                idx_to_remove = []
                for idx, row in enumerate(table_content["table_data"]):
                    
                    stripped_values = [value.strip() for value in row.values()]
                    
                    if any(x in stripped_values for x in ["Meter Type", "Meter Number", "Meter Size", "Reading", "Thousands", "(Inches)", "ESTIMATED"]):
                        idx_to_remove.append(idx)
                        
                table_content["table_data"] = [j for i, j in enumerate(table_content["table_data"]) if i not in idx_to_remove]

                '''Get previous read date from foi'''
                #Taking the first page
                previous_date = ""
                base_location = smartextract_jsons[0]['hits']['hits'][0]['_source']['data']                
                for d in base_location:
                    if d['field'] == 'previous_read_date':
                        if not 'answer' in d:
                            break
                        if len(d['answer']) == 0:
                            break
                        previous_date = ""
                        for answer in d['answer']: 
                            previous_date += answer["text"]
                            
                # @todo vendor name 
                # for field_info in smartextract_jsons[0]['hits']['hits'][0]['_source']['data']                :
                #     if field_info["field"] == "vendor_name":
                #         vendor_name_ = [{"box":{'W': 58, 'X': 1010, 'H': 29, 'Y': 1838},
                #                         "ocr_score":0.991,
                #                         "score":0.9911671876907349,
                #                         "text":"City Of Houston"}]   
                #         field_info["answer"] = vendor_name_


                for idx, row in enumerate(table_content["table_data"]):

                    service_value = table_content["table_data"][idx]["0"].strip()
                    #print("service_value--->",table_content["table_data"][idx])
                    
                    table_content.get("table_data")[idx]["0"] = mapping_service.get(service_value,"")
                    #table_content.get("table_data")[idx]["5"] = stripped_values[-2]
                    table_content.get("table_data")[idx]["7"] = previous_date
                    table_content.get("table_data")[idx]["8"] = mapping_sub_service.get(service_value,"")
                    table_content.get("table_data")[idx]["9"] = "kGal"
                    table_content.get("table_data")[idx]["10"] = ""
                    table_content.get("table_data")[idx]["11"] = ""
                    table_content.get("table_data")[idx]["12"] = ""                    

                header_row = {}
                header_row["0"] = "homst" #serviceType
                header_row["1"] = "homN"  #meterNumber
                header_row["2"] = ""
                header_row["3"] = "homRP" #meterReadPrevious
                header_row["4"] = "homRC" #meterReadCurrent
                header_row["5"] = "houbm" #usageByMeter
                header_row["6"] = "hosped" #servicePeriodEndDate
                header_row["7"] = "hospsd" #servicePeriodStartDate
                header_row["8"] = "homsst" #subServiceType
                header_row["9"] = "houom" #uom
                header_row["10"] = "homm" #meterMultiplier
                header_row["11"] = "hopf" #powerFactor
                header_row["12"] = "hodu" #demandUsage'''
                
                table_content.get("table_data").insert(0, header_row)

            if table_content.get("table_identified") == "charges_table" and table_content.get("table_data"):
                #charges table
                
                for idx, row in enumerate(table_content["table_data"]):
                    #table data 
                    description = row["0"].lower().strip().split()
                    if "fireline" in description:
                        row["2"] = "WATER"
                        row["3"] = "FIRELINE"
                    elif "drainage" in description:
                        row["2"] = "WATER"
                        row["3"] = "DRAINAGE"
                    elif any(x in description for x in ['water', 'evaporation', 'tceq']):
                        row["2"] = "WATER"
                        row["3"] = "WATER"
                    elif "irrigation" in description:
                        row["2"] = "WATER"
                        row["3"] = "IRRIGATION"
                    elif "sewer" in description:
                        row["2"] = "WATER"
                        row["3"] = "SEWER"
                    else:
                        row["2"] = ""
                        row["3"] = ""

                table_content.get("table_data").insert(0, {'0': 'hodes', #charges_description_corpus_cristi
                                                        '1': 'hocost', #charges cost_corpus_cristi
                                                        '2': 'hoServ', #charges ServiceType_corpus_cristi
                                                        '3': 'hosubS'}) #charges subServiceType_corpus_cristi
                        
                #column bounds
                last_value_charges = table_content["column_bounds"][-1]
                
                for i in range(2):
                    new_value = {
                        'y1': last_value_charges['y1'],
                        'x1': last_value_charges['x2'] + (i * 10),
                        'y2': last_value_charges['y2'],
                        'x2': last_value_charges['x2'] + ((i + 1) * 10)
                    }
                                        
                    table_content["column_bounds"].extend([new_value])
                
                #table data boxes
                table_content["table_data_boxes"]=[]
                # for row in table_content["table_data_boxes"]:
                #     fields_to_add = ["ServiceType","subServiceType"]
                #     for idx, field in enumerate(fields_to_add):
                #         row[2+idx]=[{"ocr_score":0.9,"word":field,"coords":{'y1': 0, 'x1': 0, 'y2': 0, 'x2': 0}}] 

            
    return input_tables_data,smartextract_jsons